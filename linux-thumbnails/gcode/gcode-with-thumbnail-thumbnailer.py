#!/usr/bin/env python3
#
# gcode-with-thumbnail-thumbnailer.py - A Gnome 3 thumbnailer for gcode with an embedded thumbnail
#
#    Copyright (C) 2022 Peter Ellens <ellensp@hotmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/gpl>.

#    # Contains code from the jpg re-encoder thumbnail post processor script:
#    https://raw.githubusercontent.com/alexqzd/Marlin/Gcode-preview/Slicer%20post-processing%20scripts/PrusaSlicer_JPEG_Preview.py
#    and  https://github.com/MestreLion/icns-thumbnailer

# added some fixes for JPEG/PNG and GLib

import sys
import re
import base64
import io
import subprocess
from gi.repository import GLib


try:
    from PIL import Image
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

try:
    from gi.repository import GLib
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygobject"])
    from gi.repository import GLib


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def make_thumbnail(inputname, outputname, size=0):
    try:
        sourceFile = sys.argv[1]
        # Read the ENTIRE g-code file into memory
        with open(sourceFile, "r") as f:
            lines = f.read()
        f.close()

        thumb_expresion = "; thumbnail begin.*?\n((.|\n)*?); thumbnail end"
        size_expresion = "; thumbnail begin [0-9]+x[0-9]+ [0-9]+"
        size_expresion_group = "; thumbnail begin [0-9]+x[0-9]+ ([0-9]+)"

        thumb_matches = re.findall(thumb_expresion, lines)

        if not thumb_matches:
            sys.stderr.write("gcode: Thumbnail data not found in %s\n" % sourceFile)
            return 1

        for idx, match in enumerate(thumb_matches):
            original = match[0]
            encoded = original.replace("; ", "")
            encoded = encoded.replace("\n", "")
            encoded = encoded.replace("\r", "")
            decoded = base64.b64decode(encoded)
            pixbuf = Image.open(io.BytesIO(decoded))

        if size:
            width, height = pixbuf.size
            if width > height:
                if width > size:
                    height = height * size / width
                    width = size
            else:
                if height > size:
                    width = width * size / height
                    height = size

            scaled = pixbuf.resize((int(width), int(height)), Image.LANCZOS)
        else:
            scaled = pixbuf
        # drop alpha channel if saving as jpeg
        rgb_im = scaled.convert("RGB")
        rgb_im.save(outputname)
        sys.stderr.write("gcode: Thumbnail saved: %s\n" % outputname)

    except GLib.GError as e:
        sys.stderr.write("%s:%d: %s\n" % (e.domain, e.code, e))
        return e.code


def main(argv):
    try:
        args = argv[1], argv[2], int((argv[3:4] or [0])[0])
        if len(argv) > 4:
            raise IndexError
    except (ValueError, IndexError):
        sys.stderr.write("gcode: Usage: %s inputfile outputfile [size]\n" % argv[0])
        return 1

    sys.stderr.write("gcode: Processing %s\n" % ", ".join(f'"{w}"' for w in argv))
    return make_thumbnail(*args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
