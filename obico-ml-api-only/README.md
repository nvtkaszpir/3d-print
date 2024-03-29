# obico-ml-api-only

Spawn [Obico ML API](https://www.obico.io/docs/server-guides/) container without any authentication
or any other Obico apps. This is for people that REALLY just want to have an API
for image detections, which can be further scripted with other tools.

Container image is from my modified app version:

- extra debug messages
- send more details to statsd
- allow passing ignored zones to avoid false positives due to the areas in the
  camera that contains problematic items (especially timestamps or some cables)

The AI model is left as is. You can find git sha which was used for builds in
[this repo](https://github.com/nvtkaszpir/obico-server/), the built images
are pushed to [quay.io](https://quay.io/repository/kaszpir/ml_api?tab=tags)
based on `<git-short-sha>-<arch>`. I mainly push to `dockerfile-cleanups` branch
in there.

## Usage

Just feed it with a param to fetch image to process if it is able to detect
spaghetti. Output from the API is in JSON.

```shell
docker-compose up
```

Notice that container image size is about 3GB.
Docker compose up will spawn container which listens on port `3333`.

In general Obico ML API needs to get `img` param which tells it to fetch image from
given URL to be processed. So you need a HTTP server to host the image, which
will be consumed by python app that runs within the Obico ML API container.

The target url can be also a real working camera if it is able to return image per se -
for example [esphome web server](https://esphome.io/components/esp32_camera_web_server.html)
with `snapshot` mode will work.

### Install dependencies

To run additional script `draw_detections.py` you may need some local dependencies:

```shell
pip install -r requirements.txt

```

### Draw detections with preview

For pure example purposes replace `https://bagno.hlds.pl/obico/bad_1.jpg` with the url to the image from the camera.
The URL must point to the address that is resolvable and reachable by the processes within the container.

<!-- markdownlint-disable html line-length -->

```shell
python3 draw_detections.py --api http://127.0.0.1:3333 https://bagno.hlds.pl/obico/bad_1.jpg --show

INFO:root:api=http://127.0.0.1:3333
INFO:root:show=True
INFO:root:url=https://bagno.hlds.pl/obico/bad_1.jpg
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): bagno.hlds.pl:443
DEBUG:urllib3.connectionpool:https://bagno.hlds.pl:443 "GET /obico/bad_1.jpg HTTP/1.1" 200 999433
DEBUG:urllib3.connectionpool:Starting new HTTP connection (1): 127.0.0.1:3333
DEBUG:urllib3.connectionpool:http://127.0.0.1:3333 "GET /p/?img=https%3A%2F%2Fbagno.hlds.pl%2Fobico%2Fbad_1.jpg HTTP/1.1" 200 853
[["failure", 0.502, [758.0, 969.0, 113.0, 160.0]], ["failure", 0.44, [1012.0, 959.0, 121.0, 174.0]], ["failure", 0.241, [1034.0, 1066.0, 120.0, 176.0]], ["failure", 0.238, [939.0, 967.0, 134.0, 161.0]], ["failure", 0.174, [921.0, 1062.0, 164.0, 184.0]], ["failure", 0.163, [797.0, 1051.0, 117.0, 154.0]], ["failure", 0.1, [801.0, 1140.0, 140.0, 86.0]]]

```
<!-- markdownlint-enable html line-length -->

![example](./example.png)
(No the printer is not skewed, this is the effect of camera lens distortion because it is not perpendicular to the bed)

### Draw detections without preview

You can run parameters such as `--saveimg` and `--savedet` to save output to files without preview, for easier scripting:

<!-- markdownlint-disable html line-length -->
```shell
python3 draw_detections.py --api http://127.0.0.1:3333 https://bagno.hlds.pl/obico/bad_1.jpg --savedet out.json --saveimg out.jpg
```
<!-- markdownlint-enable html line-length -->

and it should produce output such as:

- [out.json](./out.json)
- [out.jpg](./out.jpg)

With additional options `--show-below-treshold`:
<!-- markdownlint-disable html line-length -->
```shell
python3 draw_detections.py --api http://127.0.0.1:3333 https://bagno.hlds.pl/obico/bad_1.jpg --savedet out-below.json --saveimg out-below.jpg --show-below-treshold
```
<!-- markdownlint-enable html line-length -->

you should see blue areas that are below treshold:

- [out.json](./out-below.json)
- [out.jpg](./out-below.jpg)

With option `--treshold=0.4`:
<!-- markdownlint-disable html line-length -->
```shell
python3 draw_detections.py --api http://127.0.0.1:3333 https://bagno.hlds.pl/obico/bad_1.jpg --savedet out-t04.json --saveimg out-t04.jpg --treshold=0.4
```
<!-- markdownlint-enable html line-length -->

You will see only specific areas:

- [out.json](./out-t04.json)
- [out.jpg](./out-t04.jpg)

### Pass on ignored regions

add `--ignore="[json_table]"` to ignore certain regions.

Imagine you have source image 800x600, then we want to exclude left half of
the image. In normal coords this is (x=0,y=0 top left image corner)
x=0, y=0, w=400, h=300
but in the 'detections' format it needs to be encoded as `center of the box x`,
`center of the box y`, `box width`, `box height`, so our coords are:
(half, half, width, height)
xc=200, y=150, w=400, h=300

and for bound box with corners top_left=10,20, bottom_right=30,40
it would be:
xc=(30-10)/2
yc=(40-20)/2
w=30-10
h=40-20

Let say I have such regions to ignore:

```json
[
  [320, 32, 640, 64], // top left corner with timestamp
  [210, 600, 420, 1200], // left area with cables
  [1500, 600, 200, 1200] // right are with cables
]
```

The parameter passed is

`[[320, 32, 640, 64],[210, 600, 420, 1200],[1500, 600, 200, 1200]]`

So I can just run the command as:

```shell
python3 draw_detections.py \
  --api http://obico-ml-api.intra.hlds.pl/ \
  http://192.168.1.10:1880/camera/0461c8.jpg \
  --show \
  --ignore="[[320, 32, 640, 64],[210, 600, 420, 1200],[1500, 600, 200, 1200]]"
```

### Other notes

Notice that TRESHOLD value by default is `0.2` (as in default for obico ml_api)
Color codes:

- blue - below TRESHOLD (drawn only if you use `--show-below-treshold`)
- green - above TRESHOLD
- red - above 2x TRESHOLD, usually model is REALLY sure there is a spaghetti
- black -  detection in dead zone as defined in `draw_detections.py`

Notice that ml_api is processing whole image, so my example image above with
the date, can trigger false spaghetti detections :)

## Example Node-RED flow

I use it with [Node-RED](https://nodered.org/) custom flow to fetch image from
cameras and send notifications. The flow is not published yet.

- obico ml_api runs in container which exposes API via given port without any auth (this repo)
- Node-RED flow fetches images from esp32-camera (but could be from any camera)
- the image is available as static content via Node-RED at specific endpoint
- Node-RED flow does http request to `ml_api` with param to fetch image which was just a moment ago fetched by Node-RED itself
- in response there is a JSON with list of detections if any
- that responses is processed by Node-RED function + specific node so if the trigger level is reached
  then new message is generated
- that generated message can be routed to anything you like, so I chose discord,
  but could be other action if needed, for example send web call to Prusa printer
  to stop the print (but watch out for false positives)

```mermaid
sequenceDiagram
    node-red->>printer_api: check if printer prints
    node-red->>esp32cam: fetch camera image
    esp32cam->>node-red: save camera image to be accessible as static content
    node-red->>obico_ml_api: send request to process image
    obico_ml_api->>node-red: response with detections list
    node-red->>node-red: process detections list
    node-red->>discord: send message to Discord

```
