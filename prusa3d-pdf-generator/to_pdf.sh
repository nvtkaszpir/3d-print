#!/usr/bin/env bash

# set desired browser to convert web page to pdf,
# should work with chromium or google-chrome only,
# not tested with chromium :)
: "${BROWSER:=google-chrome}"


# small sanity checks
which lynx || { echo "ERROR: missing lynx, please install it on the system"; exit 1;}
which "${BROWSER}" || { echo "ERROR: missing ${BROWSER}, please install it on the system"; exit 1;}

# default input is prusaslicer.html
: "${INPUT:=prusaslicer.html}"

# articles are under https://help.prusa3d.com/article/... (or http)
lynx -dump -listonly -hiddenlinks=listonly -nonumbers "${INPUT}" | grep com/article | sort | uniq > urls.txt

# where to store output pdf files
output_dir=$(basename "${INPUT}" .html)
mkdir -p "${output_dir}"

# let's do this
echo "lines:"
wc -l urls.txt

readarray urls < urls.txt
index=0
for url in "${urls[@]}";do
    index=$((index+1))
    echo "${index}"
    filename=$(basename "${url}")
    # chrome params https://peter.sh/experiments/chromium-command-line-switches/
    ${BROWSER} --incognito --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="${output_dir}/${filename}.pdf" "${url}"
done
