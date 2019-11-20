# Web interface for gwas2vcf

Web interface for processing GWAS summary data to VCF format

## Install

```sh
git clone --recurse-submodules git@github.com:MRCIEU/gwas2vcfweb.git
cd gwas2vcfweb
docker-compose -p gwas2vcfweb -f ./docker-compose.yml up -d
```