.PHONY: all metrics commit push

all: metrics commit push

metrics:
	./metrics.sh

commit:
	git add . && git commit -m "Update prusa3d-metrics-list"

push:
	git push -u origin master
