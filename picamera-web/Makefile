GIT_COMMIT := $(shell git rev-parse --short HEAD)
GIT_SOURCE := $(shell git config --get remote.origin.url)

SHELL := /bin/bash


help:
	@grep -E '(^[0-9a-zA-Z_-]+:.*?##.*$$)|(^##)' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

version: ## show git version
	@echo GIT_COMMIT is $(GIT_COMMIT)

deps: ## install dependencies
	pip3 install -r requirements.txt

deps-dev: ## install dependencies for development
	sudo apt install -y libcap-dev
	pip3 install -r requirements-dev.txt

fmt: ## run black
	black app.py

install: ## install systemd service
	sudo cp -f picamera-web.service /lib/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable picamera-web
	sudo systemctl start picamera-web
	sudo systemctl status picamera-web

uninstall: ## uninstall systemd service
	sudo systemctl disable picamera-web
	sudo systemctl stop picamera-web
	sudo rm -f /lib/systemd/system/picamera-web.service
	sudo systemctl daemon-reload

web: ## run web server directly
	SLEEP_TIME=1 \
	gunicorn --disable-redirect-access-to-syslog --error-logfile - --access-logfile - --reload --bind 0.0.0.0:8090 --workers 1 app

web_hromex: ## run web server directly
	SLEEP_TIME=1 \
	IMAGE_X=1920 \
	IMAGE_Y=1080 \
	IMAGE_HFLIP=True \
	IMAGE_VFLIP=True \
	TUNING=ov5647_noir.json \
	gunicorn --disable-redirect-access-to-syslog --error-logfile - --access-logfile - --reload --bind 0.0.0.0:8090 --workers 1 app

web_extra: ## run web server directly with extra params
	SLEEP_TIME=2 \
	IMAGE_X=1920 \
	IMAGE_Y=1080 \
	IMAGE_HFLIP=True \
	IMAGE_VFLIP=True \
	gunicorn --disable-redirect-access-to-syslog --error-logfile - --access-logfile - --reload --bind 0.0.0.0:8090 --workers 1 app

web_nodelay: ## run web server directly with extra params
	SLEEP_TIME=0 \
	IMAGE_X=1920 \
	IMAGE_Y=1080 \
	IMAGE_HFLIP=True \
	IMAGE_VFLIP=True \
	gunicorn --disable-redirect-access-to-syslog --error-logfile - --access-logfile - --reload --bind 0.0.0.0:8090 --workers 1 app

rsync: ## rsync files to my rpi4
	rsync -av . pi@hormex:src/3d-print/picamera-web/

rinfo: ## fetch remote info
	curl http://hormex:8090/info

rimg: ## fetch remote image
	curl http://hormex:8090/ -o image.jpg
	file image.jpg

.PHONY: help version deps deps-dev fmt install web rsync
