#!/bin/sh

# enable telnet
telnetd

# enable rtsp server over lan if it is not set
if ! grep rtsp_server_mode /userdata/xhr_config.ini ; then
    echo >> /userdata/xhr_config.ini
    echo '[config]' >> /userdata/xhr_config.ini
    echo 'rtsp_server_mode=2' >> /userdata/xhr_config.ini
fi

# enable rtsp server over lan if it is set to incorrect version
if ! grep 'rtsp_server_mode=2' /userdata/xhr_config.ini ; then
    sed -i 's/rtsp_server_mode=.*/rtsp_server_mode=2/' /userdata/xhr_config.ini
fi

# max video quality
if ! grep 'video_quality=7' /userdata/xhr_config.ini ; then
    sed -i 's/video_quality=.*/video_quality=7/' /userdata/xhr_config.ini
fi

# copy current config to the microSD card for inspection
mkdir -p /mnt/sdcard/userdata/current/
cp /userdata/* /mnt/sdcard/userdata/current/


# create logs directory
mkdir -p /mnt/sdcard/logs

# create timelapse directory
mkdir -p /mnt/sdcard/timelapse

sync

# FAILOVER START
# uncomment below to get a normal app run as it should be for 1 hour

# ifconfig > /mnt/sdcard/ifconfig_before.log
# route -n > /mnt/sdcard/route_before.log
# spawn main app in the background to have a wifi
# lp_app --noshell --log2file /mnt/sdcard/logs &
# sleep 30 # wait for wifi
# ifconfig > /mnt/sdcard/ifconfig_after.log
# route -n > /mnt/sdcard/route_after.log
# sleep 3600
# killall lp_app

# FAILOVER END

# unmount sdcard and mount with +x permissions so we can execute binaries from it directly
umount /mnt/sdcard
mount -t vfat -o rw,uid=0,gid=0,dmask=000,fmask=000 /dev/mmcblk1p1 /mnt/sdcard

# copy loop script to temp dir and run from there
cp /mnt/sdcard/sync_loop.sh /tmp/ >> /mnt/sdcard/debug.log
chmod +x /tmp/sync_loop.sh >> /mnt/sdcard/debug.log

# run sync loop
/tmp/sync_loop.sh >> /mnt/sdcard/debug.log
