.PHONY: install 3mf gcode stl

install: 3mf gcode stl kill_thunar

## kill thunar (and tublerd which is auto spawned with it)
kill_thunar:
	thunar -q

# install mimetype for 3mf files, 3mf thumbnail extration script
# assign 3mf thumbnail with given thumbnail generator
3mf:
	mkdir -p ~/.local/share/mime/packages/
	cp -f 3mf/application-x-3mf.xml ~/.local/share/mime/packages/application-x-3mf.xml
	update-mime-database ~/.local/share/mime

	mkdir -p ~/.local/bin
	cp -f 3mf/3mf-thumbnailer.py ~/.local/bin/3mf-thumbnailer.py
	chmod +x ~/.local/bin/3mf-thumbnailer.py

	mkdir -p ~/.local/share/thumbnailers/
	cp -f 3mf/3mf.thumbnailer ~/.local/share/thumbnailers/3mf.thumbnailer


# install gcode thumbnail extration script
# assign gcode thumbnail with given thumbnail generator
gcode:
	mkdir -p ~/.local/bin
	cp -f gcode/gcode-with-thumbnail-thumbnailer.py ~/.local/bin/gcode-with-thumbnail-thumbnailer.py
	chmod +x ~/.local/bin/gcode-with-thumbnail-thumbnailer.py

	mkdir -p ~/.local/share/thumbnailers/
	cp -f gcode/gcode.thumbnailer ~/.local/share/thumbnailers/gcode.thumbnailer


# install stl thumbnail extration script
# assign stl thumbnail with given thumbnail generator
stl:
	mkdir -p ~/.local/bin
	cp -f stl/stl-thumbnailer.sh ~/.local/bin/stl-thumbnailer.sh
	chmod +x ~/.local/bin/stl-thumbnailer.sh

	mkdir -p ~/.local/share/thumbnailers/
	cp -f stl/stl.thumbnailer ~/.local/share/thumbnailers/stl.thumbnailer
