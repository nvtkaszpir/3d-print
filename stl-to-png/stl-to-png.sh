#!/usr/bin/env bash

# process STL files and generate PNG files per layer, using prusa-slicer

# see
#  prusa-slicer --help-sla
# for more options

prusa-slicer --sla --layer-height 0.5 --scale 0.5 --center 50,35 --rotate 90 --no-pad-enable --no-supports-enable "$1"

zip_file=$(basename "$1" .stl)
unzip -o "${zip_file}.sl1" -d "${zip_file}"

rm -f "${zip_file}.sl1"
