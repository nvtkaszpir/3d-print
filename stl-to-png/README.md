# stl-to-png

Using [PrusaSlicer](https://github.com/prusa3d/PrusaSlicer)
it is possible to slice STL files and generate a series of PNG images.

Example [skull_w_jaw.stl](https://www.printables.com/model/2770-human-skull-anatomically-correct) to merged images:

![skull_w_jaw](./skull_w_jaw.gif)

## About

This can be useful in for example wood works, when you want to convert
model to an actual physical object from a series of planks, where each plank
is cut to the shape of each layer.

The output files can be printed on the normal paper printer and then the shapes
can be transferred to planks, and then wood fragments cut from the planks
can be stacked together, glued and finished with other tools to make a wooden
sculpture.

## Known limitations

I just did quickest option to render model to images, it has some limitations,
such as:

- tested with STL files only
- remember to adjust layer height so it is the size od the planks you have
- need to adjust model scale and position accordingly (center, rotate)
- using default profile for the SLS printer (portrait, 4k resolution etc)
- output images must be scaled to the paper print area, keep each scale equal

## Further work

### Using PrusaSlicer interactively

It is possible to do it better with normal PrusaSlicer and creating
custom printer on the base of SL1S. This way you can get much better control of
what is happening, especially to reposition the model, layer height,
remove supports and padding etc.
Slice and export SL1 file and then rename it to .zip and unpack, and you have
a bunch of files you can process and print on paper printer.

## Merging images to video

You can merge generate PNG files to video using [ffmpeg](https://ffmpeg.org/)

Notice that it is best to increase framerate if you have lower layer height and
thus more images, so for example instead of 15FPS you can set 30FPS
( just change `-r 15` to `-r 30`).

MP4:

```shell
find . -maxdepth 1 -name '*.png' -print | sort -V > files.txt
sed -i -e "s/^/file '/" files.txt
sed -i -e "s/$/'/" files.txt
ffmpeg -r 15 -f concat -safe 0 -i files.txt -y -c:v libx264 -crf 20 -vf format=yuv420p -movflags +faststart output.mp4

```

GIF:

```shell
find . -maxdepth 1 -name '*.png' -print | sort -V > files.txt
sed -i -e "s/^/file '/" files.txt
sed -i -e "s/$/'/" files.txt
ffmpeg -r 15 -f concat -safe 0 -i files.txt -vf scale=320:-1 output.gif
```
