"""render detections from ml_api and return as image

useful for calling via curl or other tools

"""
import io
import flask
import draw_detections
from statsd.defaults.env import statsd
from os import environ

application = flask.Flask(__name__)

STATSD_HOST = environ.get("STATSD_HOST", "127.0.0.1")
STATSD_PORT = environ.get("STATSD_PORT", "8125")
STATSD_PREFIX = environ.get("STATSD_PREFIX", "obico.render")
STATSD_MAXUDPSIZE = environ.get("STATSD_MAXUDPSIZE")
STATSD_IPV6 = environ.get("STATSD_IPV6", "0")

application.logger.info(f"STATSD_HOST={STATSD_HOST}")
application.logger.info(f"STATSD_PORT={STATSD_PORT}")
application.logger.info(f"STATSD_PREFIX={STATSD_PREFIX}")
application.logger.info(f"STATSD_MAXUDPSIZE={STATSD_MAXUDPSIZE}")
application.logger.info(f"STATSD_IPV6={STATSD_IPV6}")


@application.route("/", methods=["GET"])
def info():
    """show usage as default page"""
    filename = "info.html"
    return flask.send_file(filename, mimetype="text/html")


@statsd.timer("do_render")
@application.route("/r/", methods=["GET"])
def render():
    """render detections and return as image

    img: url
    api: url
    ignore: json
    """
    ignore = []
    if "ignore" in flask.request.args:
        ignore = flask.request.args["ignore"]

    img = ""
    if "img" in flask.request.args:
        img = flask.request.args["img"]

    api = ""
    if "api" in flask.request.args:
        api = flask.request.args["api"]

    image = draw_detections.process_image(
        img_url=img, api=api, ignore=ignore, returnimg=True
    )
    mem = io.BytesIO()
    image.save(mem, "JPEG")
    mem.seek(0)
    image.close()
    return flask.send_file(
        mem, as_attachment=False, download_name="render.jpg", mimetype="image/jpg"
    )


# health check and readiness endpoint
@application.route("/ready", methods=["GET"])
def health_check():
    """app health check

    frankly speaking not much to return in here
    """
    return "ok"


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=3334, threaded=False)
