# prusa3d help pdf generator

Fetch pages from help.prusa3d.com and make them as PDF for offline reading.

<!-- markdownlint-disable html line-length -->
<img src="https://upload.wikimedia.org/wikipedia/commons/8/87/PDF_file_icon.svg" width="16px" alt="PDF icon"> + <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcci_ihHlaQrtKYWEQe0PbDgoJBWvWhtkoY5kAg7v4bsBeiQVR43_qeU1X3_9aCTgAwFE&usqp=CAU" height="16px" alt="Josef Prusa"> =
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Heart_coraz%C3%B3n.svg/1280px-Heart_coraz%C3%B3n.svg.png" height="16px" alt="Love">
<!-- markdownlint-enable html line-length -->

## Requirements

- Linux operating system
- `google-chrome` or `chromium`
- `lynx` cli web browser

## How to process

1. go to [PrusaSlicer help page](https://help.prusa3d.com/article/download-prusaslicer_2220)
2. on the left menu click on menus to expand all of them (pro tip: star from the bottom)
3. save page as `prusaslicer.html` in this directory (we need html file only)
4. run `./to_pdf.sh` and wait, output pdf files are under `prusaslicer/` directory

You can also process other articles, just do as above and save as `mini.html`
and then run `INPUT=mini.html ./to-pdf.sh`

## Todo

- process [help API](https://help.prusa3d.com/api/v1/helps?lng=en&page=1&per_page=9999&category=configuration-and-profiles_207)
  and extract articles?
