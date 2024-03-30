help:
	@grep -E '(^[0-9a-zA-Z_-]+:.*?##.*$$)|(^##)' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

example: ## run example image prediction agains 0.0.0.0:3333 and known bad file
	python3 draw_detections.py --api http://0.0.0.0:3333/ http://bagno.hlds.pl/obico/bad_1.jpg --saveimg example.png

example_0461c8: ## run example image prediction agains 0.0.0.0:3333 and known bad file
	python3 draw_detections.py --api http://0.0.0.0:3333/ http://bagno.hlds.pl/obico/0461c8.jpg --saveimg example_0461c8.png --ignore="[[320, 32, 640, 64],[210, 600, 420, 1200],[1500, 600, 200, 1200]]"

no_preview: ## process bad_1.jpg and save output to files
	python3 draw_detections.py --api http://127.0.0.1:3333 https://bagno.hlds.pl/obico/bad_1.jpg --savedet out.json --saveimg out.jpg

below_tresh: ## process bad_1.jpg and save output to files, also draw detections below treshold
	python3 draw_detections.py --api http://127.0.0.1:3333 https://bagno.hlds.pl/obico/bad_1.jpg --savedet out-below.json --saveimg out-below.jpg --show-below-treshold

t04: ## process bad_1.jpg with treshold 0.4 and save output to files
	python3 draw_detections.py --api http://127.0.0.1:3333 https://bagno.hlds.pl/obico/bad_1.jpg --savedet out-t04.json --saveimg out-t04.jpg --treshold=0.4

live_preview: ## get my real obico instance and real node-red image fetched from espcam
	python3 draw_detections.py --api http://obico-ml-api.intra.hlds.pl http://192.168.1.10:1880/camera/0461c8.jpg --show --ignore="[[320,32,640,64],[188,600,376,1200],[1507,600,185,1200]]"

all: example example_0461c8 no_preview below_tresh t04 ## run all examples

.PHONY: help all example example_0461c8 no_preview below_tresh t04
