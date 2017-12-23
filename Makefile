
SHELL = /bin/bash

all: build package

build:
	docker build --tag lambda:latest .

package:
	docker run \
		-w /var/task/ \
		--name lambda \
		-itd \
		lambda:latest
	docker cp lambda:/tmp/package.zip package.zip
	docker stop lambda
	docker rm lambda

shell:
	docker run \
		--name lambda  \
		--volume $(shell pwd)/:/data \
		--env PYTHONPATH=/var/task/vendored \
		--env GDAL_CACHEMAX=75% \
		--env GDAL_DISABLE_READDIR_ON_OPEN=TRUE \
		--env GDAL_TIFF_OVR_BLOCKSIZE=512 \
		--env VSI_CACHE=TRUE \
		--env VSI_CACHE_SIZE=536870912 \
		--rm \
		-it \
		lambda:latest /bin/bash

clean:
	docker stop lambda
	docker rm lambda
