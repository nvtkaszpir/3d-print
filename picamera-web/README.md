# picamera-web

Minimal web app to capture and return image from raspberry pi camera.

## Known limitations

- gunicorn workers 1 is required
- accessing camera by other apps is not possible when app is running
- you should be able to get something about 0.8 requests/s if capturing 1920x1080p image

## Requirements

```shell
sudo apt-get install -y libcap-dev curl
pyenv virtialenv picam
pyenv activate picam
pip3 install -r requirements.txt
```

## Configuration

Configuration is via environmental variables.

- `CAMERA_INSTANCE` defines camera instance to use, defaults `0`, if you have CM4 with
  two cameras you can run second web server with `CAMERA_INSTANCE=1` and update scripts
  to run gunicorn on higher port to serve two cameras on different ports.

- `SLEEP_TIME` defines time to wait before taking next camera snapshot, default `0`
  which is 2 seconds. Can be `0`  if your light conditions and camera is fast,
  or increase if conditions are poor, for example `3` would be 3s.
  This allows for camera control automations to work as expected especially in low
  light conditions.

- `SNAP_FILE` defines where to locally store image on capture,
  by default it is `/dev/shm/picamera_snapshot.jpg` so we write to shared memory
  to avoid writing to disk.

- `IMAGE_HFLIP` - horizontal flip, default is `False`

- `IMAGE_VFLIP` - vertical flip, default is `False`

- `IMAGE_X` - image capture resolution `x` in pixels, default `640`

- `IMAGE_X` - image capture resolution `y` in pixels, default `480`

- `CAMERA_CONTROLS` - camera controls as json, make sure to escape any doublequotes,
  example value `"{\"ExposureTime\": 10000, \"AnalogueGain\": 1.0}"`
  default "{}"
  this is pretty expertimental and ugly and probably broken :D

## Running

Use gunicorn, because `werkzeug` tend to hang after few concurrent requests.

```shell
gunicorn  --backlog 3 --keep-alive 5 --bind 0.0.0.0:8080 --workers 1 app
```

## Fetch camera parameters

```shell
# get image directly from raspberry pi
curl http://0.0.0.0:8080/info
```

## Fetch image

```shell
# get image directly from raspberry pi
curl http://0.0.0.0:8080/ -o image.jpg

# use obico ml-api to get the image from 192.168.1.50:8080
python3 draw_detections.py --api http://127.0.0.1:3333 http://192.168.1.50:8080/ --show

```

## Other notes

See [picamera2 manual](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
