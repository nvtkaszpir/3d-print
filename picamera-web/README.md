# picamera-web

Minimal web app to capture and return image from raspberry pi camera.

Tested with rpi4 + Debian 12 (bookworm) + kernel 6 + Raspi Cam v1

```text
Linux hormex 6.6.28+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.6.28-1+rpt1 (2024-04-22) aarch64 GNU/Linux
```

## Known limitations

- gunicorn workers 1 is required
- accessing camera by other apps is not possible when app is running
- you should be able to get something about 0.8 requests/s if capturing 1920x1080p image

## Requirements

### On Raspberry Pi

```shell
sudo apt-get update && sudo apt-get install -y git
mkdir -p /home/pi/src/
cd /home/pi/src/
git clone https://github.com/nvtkaszpir/3d-print.git
cd 3d-print/picamera-web/
make install

```

### Local development

Generally note to self:

```shell
sudo apt-get install -y libcap-dev curl
pyenv virtialenv picam
pyenv activate picam
make deps-dev

make rsync
```

and on rpi (stop service first)

```shell
make web_hromex
```

then `make rsync` and gunicorn will reload the app.

## Configuration

Configuration is via environmental variables.

- `CAMERA_INSTANCE` defines camera instance to use, defaults `0`, if you have CM4 with
  two cameras you can run second web server with `CAMERA_INSTANCE=1` and update scripts
  to run gunicorn on higher port to serve two cameras on different ports.

- `SLEEP_TIME` defines time to wait before taking next camera snapshot, default `0`
  which is 0 seconds. Can be `0` if your light conditions and camera is fast,
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

- `CAMERA_CONTROLS` - camera controls as json, make sure to escape any double quotes,
  example value `"{\"ExposureTime\": 10000, \"AnalogueGain\": 1.0}"`
  default "{}"
  this is pretty experimental and ugly and probably broken :D

## Running

Use `gunicorn`, because `werkzeug` tend to hang after few concurrent requests.

```shell
gunicorn  --backlog 3 --keep-alive 5 --bind 0.0.0.0:8090 --workers 1 app
```

## Fetch camera parameters

```shell
# get image directly from raspberry pi
curl http://0.0.0.0:8090/info
```

Use this to set other env vars if needed

## Fetch image

### Curl

```shell
# get image directly from raspberry pi
curl http://0.0.0.0:8090/ -o image.jpg
```

### Use with Obico

Assuming `192.168.1.50` is the IP address of the raspberry pi then
you should be able to use `http://192.168.1.50:8090/` as a camera snapshot with
Obico.

### Obico ml-api standalone

Use [obico-ml-api-only](../obico-ml-api-only/) to get the image from `http://192.168.1.50:8090/`

```shell
python3 draw_detections.py --api http://127.0.0.1:3333 http://192.168.1.50:8090/ --show
```

Yeah this was the real reason this code was created :D

## Other notes

See [picamera2 manual](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
