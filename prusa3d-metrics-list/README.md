# prusa3d metrics list

Get all metrics exposed by Prusa Firmware Buddy from `master` branch.
Allows to easier find what metrics can be added to 3D printer and configured
to be sent to remote syslog server for further processing.
For more details see [official doc](https://github.com/prusa3d/Prusa-Firmware-Buddy/blob/master/doc/metrics.md)

## Notice

Produced metrics are from EVERY device and model, but there is no specification
which one will work on your device, so some of them are surely not supported
by your printer.

Also given metric usually depends on the firmware that is installed on your printer.

## Run it

```shell
cd prusa3d-metrics-list
./metrics.sh
```

Output is in:

- `metrics.csv` - comma separated text file
- `metrics.gcode` as copy/paste fragments to be used in custom gcode sections using [M331](https://help.prusa3d.com/pl/article/buddy-specific-g-codes_633112)
