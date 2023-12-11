#!/usr/bin/env python3

# source https://www.reddit.com/r/3Dprinting/comments/132lesb/3mf_thumbnails_on_linux/
# added extra output for better visibility of what happens


# unfinished, not tested


import sys
import zipfile


def main():
    sys.stderr.write("3mf: Processing %s\n" % ", ".join(f'"{w}"' for w in sys.argv))
    # Check if the archive path and output path were passed as arguments
    if len(sys.argv) != 3:
        sys.stderr.write(
            "3mf: Usage: {} archive_path output_path \n".format(sys.argv[0])
        )
        sys.exit(1)
    # Check if the file exists inside the archive
    with zipfile.ZipFile(sys.argv[1], "r") as archive:
        if "Metadata/thumbnail.png" in archive.namelist():
            # Extract the file to standard output without preserving the folder structure and save it to the specified output path
            with archive.open("Metadata/thumbnail.png", "r") as thumbnail:
                with open(sys.argv[2], "wb") as output:
                    output.write(thumbnail.read())
            sys.stderr.write("3mf: File extracted successfully\n")
        else:
            # Exit with an error message
            sys.stderr.write(
                "3mf: File 'Metadata/thumbnail.png' doesn't exist inside the archive\n"
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
