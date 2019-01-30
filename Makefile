
SHELL = /bin/bash

all: build package

build:
	docker build --tag lambda:latest .

package:
	docker build --tag lambda:latest .
	docker run -w /var/task/ --name lambda -itd lambda:latest /bin/bash
	docker cp lambda:/tmp/package.zip package.zip
	docker stop lambda
	docker rm lambda


test: package
	docker run \
		--name lambda \
		--volume $(shell pwd)/:/local \
		--env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
 		--env AWS_REGION=us-east-1 \
	  --env GDAL_CACHEMAX=75% \
	  --env VSI_CACHE=TRUE \
	  --env VSI_CACHE_SIZE=536870912 \
	  --env CPL_TMPDIR="/tmp" \
	  --env GDAL_DISABLE_READDIR_ON_OPEN=TRUE \
	  --env CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".TIF" \
		-itd \
		lambci/lambda:build-python3.6 bash
	docker exec -it lambda bash -c 'unzip -q /local/package.zip -d /var/task/'
	docker exec -it lambda python3.6 -c 'from tiler.elevation import APP; print(APP({"path": "/tiles/9/84/198.png", "queryStringParameters": {"shadder":"mapbox"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET", "headers": {}}, None))'
	docker stop lambda
	docker rm lambda

clean:
	docker stop lambda
	docker rm lambda
