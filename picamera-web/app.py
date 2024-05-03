"""expose picamera as image under /

apt install gunicorn
gunicorn  --backlog 3 --keep-alive 5 --bind 0.0.0.0:8080 --workers 1 app

notice you cannot use workers 2 or more with it.

By default snapshot is written to /dev/shm/picamera_snapshot.jpg
to avoid writing to storage.
You can control this path and file name with env var SNAP_FILE
"""
import logging
import os
import json
import time
import pprint
from distutils.util import strtobool
import flask
from picamera2 import Picamera2
from libcamera import Transform

# camera controls, should be a dict
controls = {}
CAMERA_INSTANCE = int(os.getenv("CAMERA_INSTANCE", default="0"))
logging.debug(f"CAMERA_INSTANCE={CAMERA_INSTANCE}")

SLEEP_TIME = float(os.getenv("SLEEP_TIME", default="0"))
logging.debug(f"SLEEP_TIME={SLEEP_TIME}")

SNAP_FILE = os.getenv("SNAP_FILE", default="/dev/shm/picamera_snapshot.jpg")
logging.debug(f"SNAP_FILE={SNAP_FILE}")

IMAGE_HFLIP = strtobool(os.getenv("IMAGE_HFLIP", default="False"))
logging.debug(f"IMAGE_HFLIP={IMAGE_HFLIP}")

IMAGE_VFLIP = strtobool(os.getenv("IMAGE_VFLIP", default="False"))
logging.debug(f"IMAGE_VFLIP={IMAGE_VFLIP}")

IMAGE_X = int(os.getenv("IMAGE_X", default="640"))
logging.debug(f"IMAGE_X={IMAGE_X}")

IMAGE_Y = int(os.getenv("IMAGE_Y", default="480"))
logging.debug(f"IMAGE_Y={IMAGE_Y}")

cam_controls = os.getenv("CAMERA_CONTROLS", default="{}")
logging.debug(f"cam_controls={cam_controls}")

CAMERA_CONTROLS = json.loads(cam_controls.strip())
logging.debug(f"CAMERA_CONTROLS={CAMERA_CONTROLS}")

TUNING = os.getenv("TUNING", default="")
logging.debug(f"TUNING={TUNING}")

application = flask.Flask(__name__)
application.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1
application.config["PROPAGATE_EXCEPTIONS"] = True

if TUNING:
    tuning = Picamera2.load_tuning_file(TUNING)
else:
    tuning = None


picam2 = Picamera2(CAMERA_INSTANCE, tuning=tuning)

# configure camera
config = picam2.create_still_configuration(
    {"size": (IMAGE_X, IMAGE_Y)},  # see /info for available resolutions
    transform=Transform(
        hflip=IMAGE_HFLIP,
        vflip=IMAGE_VFLIP,
    ),
)
picam2.align_configuration(config)  # adjust resolutions to be optimal to the sensor
picam2.configure(config)
if CAMERA_CONTROLS:
    picam2.set_controls(CAMERA_CONTROLS)


@application.route("/")
def snapshot():
    """Take camera snapshot and server as image"""
    try:
        picam2.start()
        time.sleep(SLEEP_TIME)
        picam2.capture_file(SNAP_FILE)

        return flask.send_file(
            SNAP_FILE,
            as_attachment=False,
            download_name="snapshot.jpg",
            mimetype="image/jpeg",
        )
    except Exception:
        flask.abort(500)


@application.route("/info")
def info():
    """return camera capabilities as pretty format json"""
    msg = {
        "sensor_modes": picam2.sensor_modes,
        "camera_properties": picam2.camera_properties,
    }
    return pprint.pformat(msg)


@application.route("/healthz")
def healthz():
    """Check if camera is available

    using metadata checks if the camera connection is okay wihtout making image capture

    """
    try:
        picam2.start()
        picam2.capture_metadata()
        return "ok"
    except Exception:
        flask.abort(500)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,  # Change the level to DEBUG for more detailed logging
    )

    application.run(debug=False, host="0.0.0.0", port=8090)
