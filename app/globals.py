class Globals:
    VERSION = '0.0.1'
    UPLOAD_FOLDER = '/data/gwas2vcfweb/data'
    CROMWELL_URL = 'http://cromwell:8000'
    QC_WDL_PATH = '/app/gwas2vcf.wdl'

    # host db
    RefGenomeFile = "/data/reference_genomes/released/2019-08-30/data/2.8/b37/human_g1k_v37.fasta"
    RefGenomeFileIdx = "/data/reference_genomes/released/2019-08-30/data/2.8/b37/human_g1k_v37.fasta.fai"
    DbSnpVcfFile = "/data/dbsnp/released/2019-09-11/data/dbsnp.v153.b37.vcf.gz"
    DbSnpVcfFileIdx = "/data/dbsnp/released/2019-09-11/data/dbsnp.v153.b37.vcf.gz.tbi"
    AfVcfFile = "/data/1kg/ALL.wgs.phase3_shapeit2_mvncall_integrated_v5b.20130502.sites.vcf.gz"
    AfVcfFileIdx = "/data/1kg/ALL.wgs.phase3_shapeit2_mvncall_integrated_v5b.20130502.sites.vcf.gz.tbi"
