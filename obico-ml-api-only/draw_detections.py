"""Do a API call to obico ml api and draw boxes with detections

"""
import click
import json
import requests
import logging
from urllib.request import urlopen
from PIL import Image, ImageDraw, ImageFile, ImageFont
import json

logging.basicConfig(encoding="utf-8", level=logging.DEBUG)

ML_API_HOST = "http://127.0.0.1:3333"
VISUALIZATION_THRESH = 0.2

# fix for getting images from url
ImageFile.LOAD_TRUNCATED_IMAGES = True


def threshold_to_color(threshold):
    """return color based on threshold

    threshold=0.0 - black, dead zone, explicit to ignore the value
    0 < threshold < VIS - blue, so it is below threshold, so it detects but does not trigger
    VIS <= threshold <2x VIS - green - detected
    2x VIS < threshold < 1.0 - shit is on fire, really sure it is triggering
    threshold = 1.0 - white, if you see it then AI takes over the world

    """
    if threshold == 0.0:
        return (0, 0, 0, 255)  # black, if you see this then it was in dead zone
    if 0.0 < threshold < VISUALIZATION_THRESH:
        return (0, 0, 255, 255)  # blue
    if VISUALIZATION_THRESH <= threshold < (2 * VISUALIZATION_THRESH):
        return (0, 255, 0, 255)  # green
    if (2 * VISUALIZATION_THRESH) <= threshold < 1.0:
        return (255, 0, 0, 255)  # red, means this is 2x above threshold

    return (255, 255, 255, 255)  # white


def shape_points(coords):
    """convert detection coords to points defining a shape"""
    (xc, yc, w, h) = map(int, coords)
    (x1, y1), (x2, y2) = (xc - w // 2, yc - h // 2), (xc + w // 2, yc + h // 2)
    points = (x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)

    return points


def draw_coords(draw, coords, text, color=(128, 128, 128, 255), width=3, font_size=16):
    """draw coords on the draw object, in given color"""
    points = shape_points(coords)
    (x1, y1) = points[0]  # location where to write threshold info

    draw.line(points, fill=color, width=width)
    font = ImageFont.truetype("arial", font_size)

    draw.text((x1 + width, y1 + width), text, font=font)
    logging.debug(f"draw coords={coords} text={text} color={color}")


def overlay_detections(img, detections, ignored, ignore):
    """generate image with detections as overlay boxes"""
    draw = ImageDraw.Draw(img, "RGBA")

    # draw dead zones in cyan
    for d in ignore:
        color = (0, 255, 255, 255)
        fill = (0, 255, 255, 32)
        points = shape_points(d)
        shape = [points[0], points[2]]
        draw_coords(draw=draw, text="ignore", coords=d, color=color, width=3)
        draw.rectangle(xy=shape, fill=fill, width=1)

    # draw ignored detections
    for d in ignored:
        threshold = d[1]
        color = threshold_to_color(0.0)
        text = "{:.3f}".format(threshold)
        draw_coords(draw=draw, text=text, coords=d[2], color=color, width=3)

    # draw detections
    for d in detections:
        threshold = d[1]
        color = threshold_to_color(threshold)
        text = "{:.3f}".format(threshold)
        draw_coords(draw=draw, text=text, coords=d[2], color=color, width=1)

    return img


def do_detect(raw_pic_url, api_url=ML_API_HOST, ignore=""):
    """perform image failure detection"""
    detections = []
    ignored = []
    req = requests.get(
        api_url + "/p/", params={"img": raw_pic_url, "ignore": ignore}, verify=False
    )
    req.raise_for_status()

    if "detections" in req.json():
        detections = req.json()["detections"]

    if "ignored" in req.json():
        ignored = req.json()["ignored"]

    return detections, ignored


@click.command()
@click.option(
    "--show/--no-show",
    default=False,
    help="show image with detections directly when executing (a bit annoying)",
)
@click.option(
    "show_below_treshold",
    "--show-below-treshold/--no-show-below-treshold",
    default=False,
    help="show detections below treshold on the images",
)
@click.option(
    "--api", default="http://127.0.0.1:3333", help="obico ml_api address endpoint"
)
@click.option(
    "--ignore",
    default="[]",
    help="ignored regions on the image, must be json list of lists",
)
@click.option(
    "saveimg",
    "--saveimg",
    type=click.Path(),
    help="save image with detections given file for example out.jpg",
)
@click.option(
    "savedet", "--savedet", type=click.Path(), help="save detections to given json file"
)
@click.option(
    "treshold",
    "--treshold",
    default=VISUALIZATION_THRESH,
    help=f"treshold for visualizations, notice that this is separate to obico ml_api treshold, default {VISUALIZATION_THRESH}",
)
@click.argument("img_url")
def process_image(
    img_url, show, api, ignore, saveimg, savedet, treshold, show_below_treshold
):
    """fetch image, do detection and draw detected boxes on the image"""
    logging.info(f"treshold={treshold}")
    VISUALIZATION_THRESH = float(treshold)
    logging.info(f"api={api}")
    logging.info(f"ignore={ignore}")
    logging.info(f"show={show}")
    logging.info(f"img_url={img_url}")
    logging.info(f"saveimg={saveimg}")
    logging.info(f"savedet={savedet}")

    ignore_str = ignore
    ignore_list = json.loads(ignore)
    if not all(isinstance(elem, list) for elem in ignore_list):
        logging.warn(
            f"Failed to parse ignore param as list of lists, assuming empty list."
        )
        ignore = []
        ignore_str = ""
    logging.info(f"ignore_list: {ignore_list}")

    req = requests.get(img_url, stream=True)
    req.raise_for_status()
    detections, ignored = do_detect(img_url, api, ignore_str)
    detections_json = json.dumps(detections)
    ignored_json = json.dumps(ignored)
    logging.info(f"detections: {detections_json}")
    logging.info(f"ignored: {ignored_json}")

    if savedet:
        with open(savedet, "w") as fp:
            fp.write(json.dumps(detections) + "\n")
        logging.info(f"saved detection json to {savedet}")

    if show or saveimg:
        detections_to_visualize = detections
        ignored_to_visualize = ignored
        if not show_below_treshold:
            detections_to_visualize = [
                d for d in detections if d[1] > VISUALIZATION_THRESH
            ]

        image_with_detections = overlay_detections(
            img=Image.open(req.raw),
            detections=detections_to_visualize,
            ignored=ignored_to_visualize,
            ignore=ignore_list,
        )

    if show:
        image_with_detections.show()

    if saveimg:
        image_with_detections.save(saveimg)
        logging.info(f"saved detection image to {saveimg}")


if __name__ == "__main__":
    process_image()
