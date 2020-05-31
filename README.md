# Web interface for [gwas2vcf](https://github.com/mrcieu/gwas2vcf)

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

### Reference FASTA
mkdir -p /data/reference_genomes
cd /data/reference_genomes
wget ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/b37/human_g1k_v37.fasta.gz
wget ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/b37/human_g1k_v37.fasta.fai.gz
wget ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/b37/human_g1k_v37.dict.gz
gzip -d human_g1k_v37.fasta.gz
gzip -d human_g1k_v37.fasta.fai.gz
gzip -d human_g1k_v37.dict.gz

### 1kg
mkdir -p /data/1kg
cd /data/1kg
wget ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.wgs.phase3_shapeit2_mvncall_integrated_v5b.20130502.sites.vcf.gz
wget ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.wgs.phase3_shapeit2_mvncall_integrated_v5b.20130502.sites.vcf.gz.tbi
gzip -d ALL.wgs.phase3_shapeit2_mvncall_integrated_v5b.20130502.sites.vcf.gz
gzip -d ALL.wgs.phase3_shapeit2_mvncall_integrated_v5b.20130502.sites.vcf.gz.tbi

### dbsnp
mkdir -p /data/dbsnp
cd /data/dbsnp
wget ftp://ftp.ncbi.nih.gov/snp/latest_release/VCF/GCF_000001405.25.gz
wget ftp://ftp.ncbi.nih.gov/snp/latest_release/VCF/GCF_000001405.25.gz.tbi
mv GCF_000001405.25.gz dbsnp.v153.b37.vcf.gz
mv GCF_000001405.25.gz.tbi dbsnp.v153.b37.vcf.gz.tbi

# build stack
docker-compose build --no-cache

## this hash MUST be the same as in the wdl file
cd gwas2vcf
hash=$(git rev-parse HEAD)
docker build --no-cache -t gwas2vcf:"$hash" .

# start
cd ..
docker-compose -p gwas2vcfweb -f ./docker-compose.yml up -d
```

## Test

```sh
# Run unit tests
docker exec -it gwas2vcfweb_web_1 pytest -v
```

## Usage

### Web

1. Point browser to ```http://<hostname>```. Port can be configure in the [compose file](docker-compose.yml).
2. Upload file & obtain job identifier
3. Download results for job identifier

## Citation

```
The variant call format provides efficient and robust storage of GWAS summary statistics
Matthew S Lyon, Shea J Andrews, Benjamin L Elsworth, Tom R Gaunt, Gibran Hemani, Edoardo Marcora
bioRxiv 2020.05.29.115824; doi: https://doi.org/10.1101/2020.05.29.115824
```
