#!/bin/bash
# generate thumbnail from STL file using openscad
# inspired by https://docs.xfce.org/xfce/tumbler/available_plugins#customized_thumbnailer_for_stl_content

if (($# < 3)); then
  echo "$0: input_file_name output_file_name size"
  exit 1
fi

INPUT_FILE=$1
OUTPUT_FILE=$2
SIZE=$3

if TEMP=$(mktemp --directory --tmpdir tumbler-stl-XXXXXX); then
  cp "$INPUT_FILE" "$TEMP/source.stl"
  echo 'import("source.stl", convexity=10);' > "$TEMP/thumbnail.scad"
  openscad --imgsize "512,512" -o "$TEMP/thumbnail.png" "$TEMP/thumbnail.scad" 2>/dev/null
  convert -thumbnail "$SIZE" "$TEMP/thumbnail.png" "$OUTPUT_FILE" &>/dev/null
  rm -rf $TEMP
fi
