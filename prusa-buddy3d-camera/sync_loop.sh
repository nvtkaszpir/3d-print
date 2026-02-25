#!/bin/sh

# config start

# perform sync even if the camera is streaming, default is false
SYNC_WHEN_STREAMING=false

# volume to use when playing sounds
VOLUME=60

# path to rclone executable, for example from another partition, no spaces or special chars
RCLONE_EXE=/mnt/sdcard/rclone

# rclone config to use
RCLONE_CONFIG=/mnt/sdcard/rclone.conf

# rclone log level, use capital letters, DEBUG|INFO|NOTICE|ERROR
RCLONE_LOG_LEVEL=DEBUG

# rclone log file where to write output, no spaces or special chars
RCLONE_LOG_FILE=/mnt/sdcard/rclone.log

# rclone source for images/videos/logs to sync
RCLONE_SRC=buddy3dcam:/mnt/sdcard/timelapse/

# rclone destination for file/directory move
RCLONE_DST=bagno-smb:media/prusa/

# trasnfers 1 is required because it generally is a problem on the camera
COMMON_RCLONE_OPTIONS="--inplace  --max-buffer-memory 4M --progress --checkers 1 --transfers 1 --check-first  --list-cutoff 32 --name-transform \"suffix_keep_extension=_$(date +%Y.%m.%d_%H.%M.%S)\" --delete-empty-src-dirs --use-mmap"

# advanced tweaking
# golang gc collection, keep it extremely low to prevent OOMKills, but do not set 0
GOGC=5

# config end

# rclone/camera loop
mypid=$$

sync_log() {
    echo "$(date +%Y.%m.%d_%H.%M.%S) script_pid=$mypid $*"
}

cleanup() {
    sync_log "shutdown: cleaning up"
    killall -9 lp_app
    killall -9 rclone
    sync
    simple_ao -i /oem/usr/etc/application_exit.wav -v $VOLUME
    killall -9 telnetd
    sync
    sleep 300
    exit
}

trap cleanup INT TERM
# echo ' --- press ENTER to close --- '
# read var
# cleanup

sync_log "starting..."

# core configs, do not modify
loop_time=1s

export COMMON_RCLONE_OPTIONS
export GOGC
export RCLONE_CONFIG
export RCLONE_LOG_LEVEL
export RCLONE_LOG_FILE
export RCLONE_SRC
export RCLONE_DST
export VOLUME
# main loop
while true; do

# write files to avoid data corruption
sync

# play audio if filesystem is read only, also slow down the loop
# read only filesystem means the microsd card is corrupted
if ! touch /mnt/sdcard; then
    simple_ao -i /oem/usr/etc/factory_reset.wav -v $VOLUME
    loop_time=300
    sleep $loop_time
    continue
fi

# check if lp_app is actually in the process list, if not, then spawn it and let it run in the background
# this needs to be high enough so that we get a network because it is managed by lp_app
if ! ps | grep -v grep | grep -q 'lp_app '; then
    sync_log "lp_app_check: lp_app is not running, starting"
    lp_app --noshell --log2file /mnt/sdcard/logs &
    sleep 30
    continue
fi

if [ "$SYNC_WHEN_STREAMING" = "false" ]; then

  # do nothing if the camera is streaming via rtmp
  if netstat -ln 2>&1 | grep 0.0.0.0:554 | grep -q LISTEN; then
      sync_log "rtmp_check: lp_app is streaming via rtmp, skipping actions"
      sleep $loop_time
      continue
  fi

  # do nothing if the camera is streaming via webrtc
  # udp only, no rtmp, no ntp,
  if netstat -ln 2>&1 | grep ^udp | grep -v ':554 ' | grep -v ':123 ' | grep -q 0.0.0.0 ; then
      sync_log "rtmp_check: lp_app is streaming via webrtc, skipping actions"
      sleep $loop_time
      continue
  fi

fi

# do nothing if the camera is merging images into an avi timelapse
avi_processing=$(lsof -n | grep lp_app | grep -c /mnt/sdcard/timelapse/ | grep avi | wc -l)
if [ $avi_processing -gt 0 ]; then
    sync_log "timelapse_check: lp_app is creating avi file, skipping actions"
    sleep $loop_time
    continue
fi

# do nothing if the file /mnt/sdcard/timelapse/.timelapse_videos.csv does not exist
if [ ! -f /mnt/sdcard/timelapse/.timelapse_videos.csv ]; then
    sync_log "csv_check: lp_app did not timelapse videos yet, skipping actions"
    sleep $loop_time
    continue
fi

# if /mnt/sdcard/timelapse/.timelapse_videos.csv exists then it means timelapse avi was created at least once
# then kill lp_app to free memory, and run rclone with very low settings so it will not be killed by out of memory
if [ -f /mnt/sdcard/timelapse/.timelapse_videos.csv ]; then
    sync_log "csv_check: timelapse files created!"
fi

# should prevent killing lp_app too fast
if ! ifconfig wlan0 | grep inet; then
  sync_log "wifi_check: no wifi detected, not doing sync"
  sleep 10
  continue
fi

# do not perform any sync if the /mnt/sdcard/debug.txt is on the microsd card, will keep lp_app up and running
if [ -f /mnt/sdcard/debug.txt ]; then
    sync_log "debug_check: /mnt/sdcard/debug.txt exists, not doing sync"
    sleep $loop_time
    continue
fi

# play sound so we scare the users
simple_ao -i /oem/usr/etc/as.wav -v $VOLUME
sync_log "sync: killing lpp_app"
killall lp_app
# wait for lp_app to exit, this may take a noticeable time, sometimes a minute
while ps | grep -v grep | grep -q 'lp_app ' ; do
    sync_log "kill_check: lp_app is still running, waiting"
    sleep $loop_time
done

# run rclone for jpg,avi, then csv, optionally renaming files if the already exist on target location, so that we do not overwrite them by accident
sync_log "sync: starting rclone processing, please wait"

# sync setion
# remove --name-transform to overwrite files, this will cause 'unknown_timelapse.avi' and similiar files to be overwritten, so make sure to set the print so that time lapse has a name from gcode
# keep rclone settings very low to avoid out of memory kills

# sftp specific, commented out because it is slow
#$RCLONE_EXE --log-file $RCLONE_LOG_FILE move $RCLONE_SRC $RCLONE_DST      --include '*.{avi}' --inplace  --max-buffer-memory 2M --progress --checkers 1 --transfers 1 --list-cutoff=32 --name-transform "suffix_keep_extension=_$(date +%Y.%m.%d_%H.%M.%S)" --delete-empty-src-dirs --sftp-chunk-size 255k

# recommended for smb sync, which allows 4 chunked uploads in parallel
# also mmap helps a bit but is experimental, disable it if there are crashes
# keep jpeg and avi separated, somehow mixed multipart transfers are problematic
$RCLONE_EXE --log-file $RCLONE_LOG_FILE move $RCLONE_SRC $RCLONE_DST      --include '*.{avi}' $COMMON_RCLONE_OPTIONS

# jpeg files can be in milions so maybe in the future it would be better to just wipe it without sync?
$RCLONE_EXE --log-file $RCLONE_LOG_FILE move $RCLONE_SRC $RCLONE_DST      --include '*.{jpg}' $COMMON_RCLONE_OPTIONS

# old entry, now commented out, avi and jpeg combined together
#$RCLONE_EXE --log-file $RCLONE_LOG_FILE move $RCLONE_SRC $RCLONE_DST      --include '*.{jpg,avi}' --inplace --max-buffer-memory 1M --max-connections 2 --transfers 1 --progress --check-first --checkers=1 --name-transform "suffix_keep_extension=_$(date +%Y.%m.%d_%H.%M.%S)" --delete-empty-src-dirs

# keep below two at the end, csv and log
$RCLONE_EXE --log-file $RCLONE_LOG_FILE move $RCLONE_SRC $RCLONE_DST      --include '*.{csv}' $COMMON_RCLONE_OPTIONS
# explicitly do not use log file when moving previous rclone logs
$RCLONE_EXE                             move $RCLONE_LOG_FILE $RCLONE_DST --include '*.{log}' $COMMON_RCLONE_OPTIONS

sync_log "sync: rclone processing complete"

done
