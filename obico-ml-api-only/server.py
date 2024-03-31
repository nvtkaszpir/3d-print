import draw_detections
import flask
import io

application = flask.Flask(__name__)


@application.route("/", methods=["GET"])
def info():
    info = "info.html"
    return flask.send_file(info, mimetype="text/html")


@application.route("/r/", methods=["GET"])
def render():
    """
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


# healtchcheck and readiness endpoint
@application.route("/ready", methods=["GET"])
def health_check():
    return "ok"


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=3334, threaded=False)
