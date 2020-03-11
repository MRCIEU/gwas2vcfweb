workflow gwas2vcf {

    String JobId
    String SumStatsFilename
    Int? Cases
    Int? Controls

    # host dir
    String MountDir = "/data"
    String BaseDir = "/data/gwas2vcfweb/data"

    # host db
    File RefGenomeFile
    File RefGenomeFileIdx
    File RefGenomeFileDict
    File DbSnpVcfFile
    File DbSnpVcfFileIdx
    File AfVcfFile
    File AfVcfFileIdx

    call vcf {
        input:
            MountDir=MountDir,
            VcfFileOutPath=BaseDir + "/" + JobId + "/" + JobId + "_harm.vcf.gz",
            SumStatsFile=BaseDir + "/" + JobId + "/" + SumStatsFilename,
            ParamFile=BaseDir + "/" + JobId + "/upload.json",
            RefGenomeFile=RefGenomeFile,
            RefGenomeFileIdx=RefGenomeFileIdx,
            JobId=JobId,
            Cases=Cases,
            Controls=Controls
    }
    call combine_multiallelics {
        input:
            MountDir=MountDir,
            RefGenomeFile=RefGenomeFile,
            RefGenomeFileIdx=RefGenomeFileIdx,
            VcfFileIn=vcf.VcfFile,
            VcfFileInIdx=vcf.VcfFileIdx,
            VcfFileOutPath=BaseDir + "/" + JobId + "/" + JobId + ".vcf.gz"
    }
    #call annotate_dbsnp {
    #    input:
    #        MountDir=MountDir,
    #        VcfFileIn=combine_multiallelics.VcfFile,
    #        VcfFileInIdx=combine_multiallelics.VcfFileIdx,
    #        DbSnpVcfFile=DbSnpVcfFile,
    #        DbSnpVcfFileIdx=DbSnpVcfFileIdx,
    #        VcfFileOutPath=BaseDir + "/" + JobId + "/" + JobId + "_dbsnp.vcf.gz"
    #}
    #call annotate_af {
    #    input:
    #        MountDir=MountDir,
    #        VcfFileIn=annotate_dbsnp.VcfFile,
    #        VcfFileInIdx=annotate_dbsnp.VcfFileIdx,
    #        AfVcfFile=AfVcfFile,
    #        AfVcfFileIdx=AfVcfFileIdx,
    #        VcfFileOutPath=BaseDir + "/" + JobId + "/" + JobId + "_data.vcf.gz"
    #}
    #call validate {
    #    input:
    #        MountDir=MountDir,
    #        VcfFileIn=annotate_af.VcfFile,
    #        VcfFileInIdx=annotate_af.VcfFileIdx,
    #        RefGenomeFile=RefGenomeFile,
    #        RefGenomeFileIdx=RefGenomeFileIdx,
    #        RefGenomeFileDict=RefGenomeFileDict,
    #        VcfFileOutPath=BaseDir + "/" + JobId + "/" + JobId + ".vcf.gz",
    #        VcfFileOutIdxPath=BaseDir + "/" + JobId + "/" + JobId + ".vcf.gz.tbi"
    #}

}

task vcf {

    String MountDir
    String VcfFileOutPath
    File SumStatsFile
    File RefGenomeFile
    File RefGenomeFileIdx
    File ParamFile
    String JobId
    Int? Cases
    Int? Controls

    command <<<
        set -e

        docker run \
        --rm \
        -v ${MountDir}:${MountDir} \
        --cpus="1" \
        gwas2vcf:c52e3c2631c3dcbedd66566a740fe38c9780f855 \
        python /app/main.py \
        --data ${SumStatsFile} \
        --id ${JobId} \
        --json ${ParamFile} \
        --ref ${RefGenomeFile} \
        --out ${VcfFileOutPath} \
        --rm_chr_prefix \
        ${"--cohort_cases" + Cases} \
        ${"--cohort_controls" + Controls}
    >>>

    output {
        File VcfFile = "${VcfFileOutPath}"
        File VcfFileIdx = "${VcfFileOutPath}.tbi"
    }

}

task combine_multiallelics {

    String MountDir
    File VcfFileIn
    File VcfFileInIdx
    File RefGenomeFile
    File RefGenomeFileIdx
    String VcfFileOutPath

    command <<<
        set -e

        docker run \
        --rm \
        -v ${MountDir}:${MountDir} \
        --cpus="1" \
        halllab/bcftools:v1.9 \
        bcftools norm \
        -f ${RefGenomeFile} \
        -m +any \
        -O z \
        -o ${VcfFileOutPath} \
        ${VcfFileIn}

        docker run \
        --rm \
        -v ${MountDir}:${MountDir} \
        --cpus="1" \
        halllab/bcftools:v1.9 \
        bcftools index \
        -t \
        ${VcfFileOutPath}

    >>>

    output {
        File VcfFile = "${VcfFileOutPath}"
        File VcfFileIdx = "${VcfFileOutPath}.tbi"
    }

}

task annotate_dbsnp {

    String MountDir
    File VcfFileIn
    File VcfFileInIdx
    File DbSnpVcfFile
    File DbSnpVcfFileIdx
    String VcfFileOutPath


    command <<<
        set -e

        docker run \
        --rm \
        -v ${MountDir}:${MountDir} \
        --cpus="1" \
        halllab/bcftools:v1.9 \
        bcftools annotate \
        -a ${DbSnpVcfFile} \
        -c ID \
        -o ${VcfFileOutPath} \
        -O z \
        ${VcfFileIn}

        docker run \
        --rm \
        -v ${MountDir}:${MountDir} \
        --cpus="1" \
        halllab/bcftools:v1.9 \
        bcftools index \
        -t \
        ${VcfFileOutPath}

    >>>

    output {
        File VcfFile = "${VcfFileOutPath}"
        File VcfFileIdx = "${VcfFileOutPath}.tbi"
    }

}

task annotate_af {

    String MountDir
    File VcfFileIn
    File VcfFileInIdx
    File AfVcfFile
    File AfVcfFileIdx
    String VcfFileOutPath


    command <<<
        set -e

        docker run \
        --rm \
        -v ${MountDir}:${MountDir} \
        --cpus="1" \
        halllab/bcftools:v1.9 \
        bcftools annotate \
        -a ${AfVcfFile} \
        -c AF,EAS_AF,EUR_AF,AFR_AF,AMR_AF,SAS_AF \
        -o ${VcfFileOutPath} \
        -O z \
        ${VcfFileIn}

        docker run \
        --rm \
        -v ${MountDir}:${MountDir} \
        --cpus="1" \
        halllab/bcftools:v1.9 \
        bcftools index \
        -t \
        ${VcfFileOutPath}

    >>>

    output {
        File VcfFile = "${VcfFileOutPath}"
        File VcfFileIdx = "${VcfFileOutPath}.tbi"
    }

}

task validate {

    String MountDir
    File VcfFileIn
    File VcfFileInIdx
    File RefGenomeFile
    File RefGenomeFileIdx
    File RefGenomeFileDict
    String VcfFileOutPath
    String VcfFileOutIdxPath

    command <<<
        set -e

        docker run \
        --rm \
        -v ${MountDir}:${MountDir} \
        --cpus="1" \
        broadinstitute/gatk:4.1.3.0 \
        gatk ValidateVariants \
        --validation-type-to-exclude ALLELES \
        -V ${VcfFileIn} \
        -R ${RefGenomeFile}

        # move to complete
        cp ${VcfFileIn} ${VcfFileOutPath}
        cp ${VcfFileInIdx} ${VcfFileOutIdxPath}

    >>>

    output {
        File VcfFile = "${VcfFileOutPath}"
        File VcfFileIdx = "${VcfFileOutIdxPath}"
    }
}
