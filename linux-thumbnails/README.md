# Linux thumbnails generator for 3D files

Linux thumbnail generation scripts for various files when using file managers.

## Known limitations

- no .bgcode support yet
- .3mf files must have Metadata/thumbnail.png inside to have a preview
- .gcode must have thumbnail embedded to be extracted (PrusaSlicer does that)
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

## Testing if it works

```shell
thunar -q
killall tumblerd
/usr/lib/x86_64-linux-gnu/tumbler-1/tumblerd
```

and then open Thunar and go to directory to see if it gets thumbnails
or other messages in the console:

<!-- markdownlint-disable MD013 -->

```text
gcode: Thumbnail saved: /tmp/tumbler-XJR2SF2.png
3mf: Processing "/home/kaszpir/.local/bin/3mf-thumbnailer.py", "/home/kaszpir/prusa/gridfinity/Gridfinity Pressure Fit Jig - Tight Tolerance.3mf", "/tmp/tumbler-XPH32F2.png"
3mf: File 'Metadata/thumbnail.png' doesn't exist inside the archive

```
<!-- markdownlint-enable MD013 -->

You can also run scripts directly.

```shell
3mf-thumbnailer.py empty.3mf empty.png
```

```text
3mf: Processing "/home/kaszpir/.local/bin/3mf-thumbnailer.py", "empty.3mf", "empty.png"
3mf: File extracted successfully
```
