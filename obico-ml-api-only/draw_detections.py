"""Do a API call to obico ml api and draw boxes with detections

"""
import click
import json
import requests
import logging
from urllib.request import urlopen
from PIL import Image, ImageDraw, ImageFile, ImageFont

logging.basicConfig(encoding="utf-8", level=logging.DEBUG)

ML_API_HOST = "http://127.0.0.1:3333"
VISUALIZATION_THRESH = 0.2

# fix for getting images from url
ImageFile.LOAD_TRUNCATED_IMAGES = True

# dead zones are defined as top left corner + width/height
DEAD_ZONES = [
    [320, 32, 640, 64],  # timestamps
    [210, 600, 420, 1200],  # left camera open space
    [1500, 600, 200, 1200],  # right camera open space
    [1500, 600, 198, 1200],
]  # center x, center y, width, height


def is_in_dead_zone(d):
    """return true if detected box is in dead zone

    this is required to avoid false positives dues to extra elements on the images
    such as timestamps

    Args:
        detection (_type_): _description_
        dead_zones (_type_): _description_
    """
    (xc, yc, w, h) = map(int, d)
    (x1, y1), (x2, y2) = (xc - w // 2, yc - h // 2), (xc + w // 2, yc + h // 2)

    for dead in DEAD_ZONES:
        (deadxc, deadyc, deadw, deadh) = map(int, dead)
        (deadx1, deady1), (deadx2, deady2) = (
            deadxc - deadw // 2,
            deadyc - deadh // 2,
        ), (deadxc + deadw // 2, deadyc + deadh // 2)

        # just check if the center od the detected box is in the dead zone
        if (deadx1 < xc) and (deady1 < yc):
            # If bottom-right innerbox corner is inside the bounding box
            if (xc < deadx2) and (yc < deady2):
                # print('whole box is inside dead zone')
                return True

    return False


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


def overlay_detections(img, detections):
    """generate image with detections as overlay boxes"""
    draw = ImageDraw.Draw(img)
    width = 3
    font_size = 16

    for dead in DEAD_ZONES:
        (xc, yc, w, h) = map(int, dead)
        (x1, y1), (x2, y2) = (xc - w // 2, yc - h // 2), (xc + w // 2, yc + h // 2)
        points = (x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)
        draw.line(points, fill=(0, 255, 255, 255), width=1)  # cyan for dead zones

    for d in detections:
        threshold = d[1]
        if is_in_dead_zone(d[2]):
            threshold = 0.0
        color = threshold_to_color(threshold)

        (xc, yc, w, h) = map(int, d[2])
        (x1, y1), (x2, y2) = (xc - w // 2, yc - h // 2), (xc + w // 2, yc + h // 2)
        points = (x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)

        draw.line(points, fill=color, width=width)
        font = ImageFont.truetype("arial", font_size)
        text = "{:.3f}".format(threshold)
        draw.text((x1 + width, y1 + width), text, font=font)
    return img


def do_detect(raw_pic_url, api_url=ML_API_HOST):
    """perform image failure detection"""
    req = requests.get(api_url + "/p/", params={"img": raw_pic_url}, verify=False)
    req.raise_for_status()
    detections = req.json()["detections"]
    return detections


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
@click.argument("url")
def process_image(url, show, api, saveimg, savedet, treshold, show_below_treshold):
    """fetch image, do detection and draw detected boxes on the image"""
    logging.info(f"treshold={treshold}")
    VISUALIZATION_THRESH = float(treshold)
    logging.info(f"api={api}")
    logging.info(f"show={show}")
    logging.info(f"url={url}")
    logging.info(f"saveimg={saveimg}")
    logging.info(f"savedet={savedet}")
    req = requests.get(url, stream=True)
    req.raise_for_status()
    detections = do_detect(url, api)
    detections_json = json.dumps(detections)
    logging.info(f"detections: {detections_json}")

    if savedet:
        with open(savedet, "w") as fp:
            fp.write(json.dumps(detections) + "\n")
        logging.info(f"saved detection json to {savedet}")

    if show or saveimg:
        detections_to_visualize = detections
        if not show_below_treshold:
            detections_to_visualize = [
                d for d in detections if d[1] > VISUALIZATION_THRESH
            ]

        image_with_detections = overlay_detections(
            Image.open(req.raw), detections_to_visualize
        )

    if show:
        image_with_detections.show()

    if saveimg:
        image_with_detections.save(saveimg)
        logging.info(f"saved detection image to {saveimg}")


if __name__ == "__main__":
    process_image()
