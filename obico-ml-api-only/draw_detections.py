"""Do a API call to obico ml api and draw boxes with detections

"""
import json
import logging

import click
import requests
from PIL import Image, ImageDraw, ImageFile, ImageFont

logging.basicConfig(encoding="utf-8", level=logging.DEBUG)

ML_API_HOST = "http://127.0.0.1:3333"
VISUALIZATION_THRESH = 0.2

# fix for getting images from url
ImageFile.LOAD_TRUNCATED_IMAGES = True


def threshold_to_color(threshold: float = 0.0):
    """return color based on threshold

    threshold=0.0 - black, dead zone, explicit to ignore the value
    0 < threshold < VIS - blue, so it is below threshold, so it detects but does not trigger
    VIS <= threshold <2x VIS - green - detected
    2x VIS < threshold < 1.0 - shit is on fire, really sure it is triggering
    threshold = 1.0 - white, if you see it then AI takes over the world

    Args:
        treshold(float): input treshold
    Returns:
        tuple(RGBA): RGBA color representation

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
    """convert detection coords to points defining a shape

    Args:
        coords(tuple[number]): each coord item is a list of [centerx, centery, width, height]

    Returns:
        points([tuples]): points represent a shape that is used by drawing

    """
    (xc, yc, w, h) = map(int, coords)
    (x1, y1), (x2, y2) = (xc - w // 2, yc - h // 2), (xc + w // 2, yc + h // 2)
    points = (x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)

    return points


# pylint: disable=too-many-arguments, too-many-positional-arguments
def draw_coords(
    draw: ImageDraw,
    coords,
    text: str = "",
    color=(128, 128, 128, 255),
    width: int = 3,
    font_size: int = 16,
) -> None:
    """draw coords on the draw object, in given color

    Args:
        draw(obj): Image object from Pillow to draw on
        coords(list[number]): coordinates to draw which represent [centerx, centery, width, height]
        text(str): text to draw in top left corner of the box
        color(RGBA): color used to draw the box and text
        width(int): frame width in pixels
        font_size(int): font size in pixels? to write text in top left corner

    """
    # get coords as shape, a tuple of point
    shape = shape_points(coords)

    # draw a shape, box
    draw.line(shape, fill=color, width=width)

    # draw a text in the corner
    (x1, y1) = shape[0]  # location where to write text, in here this is top left corner
    font = ImageFont.truetype("FreeMono", font_size)
    draw.text((x1 + width, y1 + width), text, font=font)

    logging.debug("draw coords=%s text=%s color=%s", coords, text, color)


def overlay_detections(img, detections, ignored, ignore):
    """generate image with detections as colored boxes overlaid on the image

    Args:
        img(file): source image, to be used as background
        detections(list): list of detections from obico ml_api
        ignored(list): list of ignored detections from obico ml_ali
        ignore(list): list of areas which are ignored with detections,
            this is the same as passed to obico ml_api

    """
    draw = ImageDraw.Draw(img, "RGBA")

    # draw ignored zones in cyan
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
        text = f"{threshold:.3f}"
        draw_coords(draw=draw, text={text}, coords=d[2], color=color, width=3)

    # draw detections
    for d in detections:
        threshold = d[1]
        color = threshold_to_color(threshold)
        text = f"{threshold:.3f}"
        draw_coords(draw=draw, text=text, coords=d[2], color=color, width=1)

    return img


def do_detect(raw_pic_url: str = "", api_url: str = ML_API_HOST, ignore: str = ""):
    """perform image failure detection by calling obico ml_api

    Args:
        raw_pic_url(str): URL to the image to process by ml_api
        api_url(str): URL to obico ml_api
        ignore(str): list of areas to ignore as string (json to string), each item
            in the list is a box in form of [centerx, cetery, width, height]

    Returns:
        detections(list): list of detections if any
        ignored(list): list of ignored detections if any were in ignore list

    """
    detections = []
    ignored = []
    req = requests.get(
        api_url + "/p/",
        params={"img": raw_pic_url, "ignore": ignore},
        timeout=10,
        verify=False,
    )
    req.raise_for_status()

    if "detections" in req.json():
        detections = req.json()["detections"]

    if "ignored" in req.json():
        ignored = req.json()["ignored"]

    return detections, ignored


# pylint: disable=too-many-arguments, too-many-locals, too-many-positional-arguments
def process_image(
    api,
    img_url,
    ignore="",
    treshold=VISUALIZATION_THRESH,
    show=False,
    saveimg="",
    savedet=False,
    show_below_treshold=False,
    returnimg=False,
):
    """fetch image, do detection and draw detected boxes on the image"""
    logging.info("treshold=%s", treshold)
    VISUALIZATION_THRESH = float(treshold)
    logging.info("api=%s", api)
    logging.info("ignore=%s", ignore)
    logging.info("show=%s", show)
    logging.info("img_url=%s", img_url)
    logging.info("saveimg=%s", saveimg)
    logging.info("savedet=%s", savedet)

    ignore_str = ignore
    ignore_list = json.loads(ignore)
    if not all(isinstance(elem, list) for elem in ignore_list):
        logging.warning(
            "Failed to parse ignore param as list of lists, assuming empty list."
        )
        ignore = []
        ignore_str = ""
    logging.info("ignore_list: %s", ignore_list)

    detections, ignored = do_detect(img_url, api, ignore_str)
    detections_json = json.dumps(detections)
    ignored_json = json.dumps(ignored)
    logging.info("detections: %s", detections_json)
    logging.info("ignored: %s", ignored_json)

    if savedet:
        with open(savedet, "w", encoding="utf-8") as fp:
            fp.write(json.dumps(detections) + "\n")
        logging.info("saved detection json to %s", savedet)

    if show or saveimg or returnimg:
        req = requests.get(img_url, stream=True, timeout=10)
        req.raise_for_status()

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
            logging.info("saved detection image to %s", saveimg)

        if returnimg:
            return image_with_detections

    return None


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
    help=f"treshold for visualizations, notice that this is separate to obico ml_api treshold, \
        default {VISUALIZATION_THRESH}",
)
@click.argument("img_url")
# pylint: disable=missing-function-docstring
def process_image_cli(
    img_url, show, api, ignore, saveimg, savedet, treshold, show_below_treshold
):
    process_image(
        img_url=img_url,
        show=show,
        api=api,
        ignore=ignore,
        saveimg=saveimg,
        savedet=savedet,
        treshold=treshold,
        show_below_treshold=show_below_treshold,
    )


if __name__ == "__main__":
    process_image_cli()  # pylint: disable=no-value-for-parameter
