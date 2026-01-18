#!/bin/sh

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

# copy current config to the microSD card for inspection
mkdir -p /mnt/sdcard/userdata/current/
cp /userdata/* /mnt/sdcard/userdata/current/

# write files to avoid data corruption
sync

# enable telnet
telnetd

# run generic Prusa app and tell it to direct logs output to microSD card under logs/ dir
lp_app --noshell --log2file /mnt/sdcard/logs
