# Web interface for gwas2vcf

Web interface for processing GWAS summary data to VCF format

## Install

```sh

# get source
git clone --recurse-submodules git@github.com:MRCIEU/gwas2vcfweb.git
cd gwas2vcfweb

# configure host

## store cromwell outputs here
mkdir -p /data/gwas2vcfweb

## upload & download from here
mkdir -p /data/gwas2vcfweb/data

## DB files
# TODO

# build & start stack
docker-compose build --no-cache
docker-compose -p gwas2vcfweb -f ./docker-compose.yml up -d
```

## Test

```sh
# Run unit tests
docker exec -it gwas2vcfweb_web_1 pytest -v
```

## Usage

### Web

1. Point browser to ```http://<hostname>:8400```. Port can be configure in the [compose file](docker-compose.yml).
2. Upload file & obtain job identifier
3. Download results for job identifier