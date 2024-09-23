GIT_COMMIT := $(shell git rev-parse --short HEAD)
GIT_SOURCE := $(shell git config --get remote.origin.url)
BASE_IMAGE := docker.io/library/python:3.12.6-slim-bookworm
BASE_DIGEST := sha256:15bad989b293be1dd5eb26a87ecacadaee1559f98e29f02bf6d00c8d86129f39
QUAY_REPO_USER ?= kaszpir
QUAY_REPO_NAME ?= obico_render

OBICO_API_ONLY ?= http://0.0.0.0:3333/

help:
	@grep -E '(^[0-9a-zA-Z_-]+:.*?##.*$$)|(^##)' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

version: ## show git version
	@echo GIT_COMMIT is $(GIT_COMMIT)

lint-dockerfile: ## Runs hadolint against application dockerfile
	docker run --rm -v "$(PWD):/data" -w "/data" hadolint/hadolint hadolint Dockerfile

docker_config: ## configure docker to allow multi-arch builds
	docker run --privileged --rm tonistiigi/binfmt --install all

obico_render_amd64: ARCH=amd64
obico_render_amd64: ## build docker image
	docker buildx build --load \
		--platform=linux/${ARCH} \
		-t obico_render:${GIT_COMMIT}-${ARCH} \
		--build-arg BASE_IMAGE=${BASE_IMAGE} \
		--build-arg BASE_DIGEST=${BASE_DIGEST} \
		--build-arg GIT_COMMIT=${GIT_COMMIT} \
		--build-arg GIT_SOURCE=${GIT_SOURCE} \
		--build-arg BASE_TAG=${GIT_COMMIT}-${ARCH} \
		-f Dockerfile .

obico_render: ## build docker images
	$(MAKE) obico_render_amd64

docker_run: ARCH=amd64
docker_run: obico_render
	docker run -it -p 3334:3334 obico_render:${GIT_COMMIT}-${ARCH}

list_images: ## list images if they were built
	@docker image ls | grep ${GIT_COMMIT}

clean: ## delete built images for current commit
	docker image ls | grep ${GIT_COMMIT} | awk '{print $$3}' | sort | uniq | xargs docker rmi -f || true

.PHONY: obico_render list_images quay quay_amd64 obico_render obico_render_amd64
all: lint-dockerfile obico_render list_images ## build all images

quay_amd64:  ARCH=amd64
quay_amd64:
	$(MAKE) obico_render_${ARCH}
	docker tag obico_render:${GIT_COMMIT}-${ARCH} quay.io/${QUAY_REPO_USER}/${QUAY_REPO_NAME}:${GIT_COMMIT}-${ARCH}
	docker push quay.io/${QUAY_REPO_USER}/${QUAY_REPO_NAME}:${GIT_COMMIT}-${ARCH}

quay: ## build docker images and push to quay.io
	$(MAKE) quay_amd64

example: ## run example image prediction agains 0.0.0.0:3333 and known bad file
	python3 draw_detections.py --api ${OBICO_API_ONLY} https://bagno.hlds.pl/obico/bad_1.jpg --saveimg example.png

example_small: example ## make example.png and cut out fragment from it with imagemagick
	convert example.png -crop 458x350+681+840 example_small.png

example_0461c8: ## run example image prediction agains 0.0.0.0:3333 and known bad file
	python3 draw_detections.py --api ${OBICO_API_ONLY} https://bagno.hlds.pl/obico/0461c8.jpg --saveimg example_0461c8.png --ignore="[[320, 32, 640, 64],[210, 600, 420, 1200],[1500, 600, 200, 1200]]"

no_preview: ## process bad_1.jpg and save output to files
	python3 draw_detections.py --api ${OBICO_API_ONLY} https://bagno.hlds.pl/obico/bad_1.jpg --savedet out.json --saveimg out.jpg

below_tresh: ## process bad_1.jpg and save output to files, also draw detections below treshold
	python3 draw_detections.py --api ${OBICO_API_ONLY} https://bagno.hlds.pl/obico/bad_1.jpg --savedet out-below.json --saveimg out-below.jpg --show-below-treshold

t04: ## process bad_1.jpg with treshold 0.4 and save output to files
	python3 draw_detections.py --api ${OBICO_API_ONLY} https://bagno.hlds.pl/obico/bad_1.jpg --savedet out-t04.json --saveimg out-t04.jpg --treshold=0.4

live_preview: ## get my real obico instance and real node-red image fetched from espcam
	python3 draw_detections.py --api ${OBICO_API_ONLY} http://192.168.1.10:1880/camera/0461c8.jpg --show --ignore="[[320,32,640,64],[188,600,376,1200],[1507,600,185,1200]]"

web: ## get my real obico instance and real node-red image fetched from espcam
	open "http://0.0.0.0:8080/r/?api=http://obico-ml-api.intra.hlds.pl&img=http://192.168.1.10:1880/camera/0461c8.jpg&ignore=%5B%5B320%2C32%2C640%2C64%5D%2C%5B188%2C600%2C376%2C1200%5D%2C%5B1507%2C600%2C185%2C1200%5D%5D"

examples: example example_small example_0461c8 no_preview below_tresh t04 ## run all examples

.PHONY: help all example example_0461c8 no_preview below_tresh t04
