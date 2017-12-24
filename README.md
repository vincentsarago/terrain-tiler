# terrain-tiler

#### AWS Lambda + Elevation AWS PDS = landsat-tiler

https://aws.amazon.com/fr/public-datasets/terrain/


# Info


---

# Installation

##### Requirement
  - AWS Account
  - Docker
  - node + npm


#### Create the package

```bash
# Build Amazon linux AMI docker container + Install Python modules + create package
git clone https://github.com/vincentsarago/terrain-tiler.git
cd terrain-tiler/
make all
```

#### Deploy to AWS

```bash
#configure serverless (https://serverless.com/framework/docs/providers/aws/guide/credentials/)
npm install
sls deploy
```

# Endpoint

#### /tiles

#### /wmts.xml
