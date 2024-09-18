#!/usr/bin/env bash
# rm -rf Prusa-Firmware-Buddy/
# git clone --depth=1 https://github.com/prusa3d/Prusa-Firmware-Buddy.git

pushd Prusa-Firmware-Buddy || exit 1
commit=$(git rev-parse HEAD)
popd || return

date=$(date --utc)
# print all metrics available in Prusa-Firmware-Buddy
echo "Name,Type,File" > metrics.csv
grep -n -r -E 'METRIC_DEF\((.*)"([^"]+)"(.*)METRIC_VALUE_([A-Z_]+)' \
| sed -E 's|(.*):.*METRIC_DEF\((.*)"([^"]+)"(.*)METRIC_VALUE_([A-Z_]+).*|\3,\5,\1|' \
| sed "s|Prusa-Firmware-Buddy\/|https://github.com/prusa3d/Prusa-Firmware-Buddy/blob/${commit}/|g" \
| sed -E 's|:([0-9]+)|#L\1|g' \
| sort | uniq >> metrics.csv
echo "# generated at ${date},# PrusaFirmwareBuddy commit=${commit},# script source https://github.com/nvtkaszpir/3d-print" >> metrics.csv


# add gcode prefixes
echo ";generated at ${date}, PrusaFirmwareBuddy commit=${commit}, script source https://github.com/nvtkaszpir/3d-print" > metrics.gcode
grep -n -r -E 'METRIC_DEF\((.*)"([^"]+)"(.*)METRIC_VALUE_([A-Z_]+)' \
| sed -E 's|(.*):.*METRIC_DEF\((.*)"([^"]+)"(.*)METRIC_VALUE_([A-Z_]+).*|M331 \3 ;metric type \5 - \1|' \
| sed "s|Prusa-Firmware-Buddy\/|https://github.com/prusa3d/Prusa-Firmware-Buddy/blob/${commit}/|g" \
| sed -E 's|:([0-9]+)|#L\1|g' \
| sort | uniq >> metrics.gcode

echo "See metrics.csv and metrics.gcode"
