# Linux thumbnails generator for 3D files

Linux thumbnail generation scripts for various files when using file managers.

## Known limitations

- Works with XFCE4 Thunar and sends requests to generate thumbnails to thumbler.
- Probbaly does not work over network shares (file manager restrictions)
- Tested in user install only (I was lazy)

## Requirements

- git
- imagemagick to convert images
- make (under Ubuntu it is in `build-essential` package)
- openscad to convert certain files to images
- python3

## Installation

Install system packages, Ubuntu example:

```shell
sudo apt-get update
sudo apt get install -y build-essential openscad python3-pip git imagemagick python3-zipp

```

Install python packages, can be as user ( no need for sudo, but then it will be
working only for given user that installed it)

```shell
pip3 install -r requirements.txt
```

Install thumbnail generators

```shell
mkdir ~/src
cd ~/src
git clone https://github.com/nvtkaszpir/3d-print.git
cd 3d-print/linux-thumbnails
make install
```
