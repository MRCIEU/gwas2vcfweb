from werkzeug.datastructures import FileStorage
import marshmallow.exceptions
import gzip
import json
import requests
import os
from globals import Globals
from flask_restplus import Api, Resource, Namespace
from gwas_row_schema import GwasRowSchema
import uuid
import logging

api = Namespace('txt', description="Convert GWAS summary stats files")


@api.route('/upload')
@api.doc(description="Upload GWAS summary stats file")
class Upload(Resource):
    parser = api.parser()

    # gwas2vcf params
    parser.add_argument('chr_col', type=int, required=True, help="Column index for chromosome")
    parser.add_argument('pos_col', type=int, required=True, help="Column index for base position")
    parser.add_argument('ea_col', type=int, required=True, help="Column index for effect allele")
    parser.add_argument('oa_col', type=int, required=True, help="Column index for non-effect allele")
    parser.add_argument('beta_col', type=int, required=True, help="Column index for effect size")
    parser.add_argument('se_col', type=int, required=True, help="Column index for standard error")
    parser.add_argument('pval_col', type=int, required=True, help="Column index for P-value")
    parser.add_argument('delimiter', type=str, required=True, choices=("comma", "tab", "space"),
                        help="Column delimiter for file")
    parser.add_argument('header', type=str, required=True, help="Does the file have a header line?",
                        choices=('True', 'False'))
    parser.add_argument('ncase_col', type=int, required=False, help="Column index for case sample size")
    parser.add_argument('snp_col', type=int, required=False, help="Column index for dbsnp rs-identifer")
    parser.add_argument('eaf_col', type=int, required=False,
                        help="Column index for effect allele frequency")
    parser.add_argument('oaf_col', type=int, required=False,
                        help="Column index for other allele frequency")
    parser.add_argument('imp_z_col', type=int, required=False,
                        help="Column number for summary statistics imputation Z score")
    parser.add_argument('imp_info_col', type=int, required=False,
                        help="Column number for summary statistics imputation INFO score")
    parser.add_argument('ncontrol_col', type=int, required=False,
                        help="Column index for control sample size; total sample size if continuous trait")
    parser.add_argument('build', type=str, choices=('GRCh37',), required=True,
                        help='Genome build used to perform the GWAS study.')
    parser.add_argument('cohort_cases', type=int, required=False,
                        help="Total number of cases used in study")
    parser.add_argument('cohort_controls', type=int, required=False,
                        help="Total number of controls used in study")

    # other args
    parser.add_argument('gwas_file', location='files', type=FileStorage, required=True,
                        help="Path to GWAS summary stats text file for upload")
    parser.add_argument('gzipped', type=str, required=True, help="Is the file compressed with gzip?",
                        choices=('True', 'False'))

    @staticmethod
    def validate_row_with_schema(line_split, args):
        row = dict()

        if 'chr_col' in args and args['chr_col'] is not None:
            row['chr'] = line_split[args['chr_col']]
        if 'pos_col' in args and args['pos_col'] is not None:
            row['pos'] = line_split[args['pos_col']]
        if 'ea_col' in args and args['ea_col'] is not None:
            row['ea'] = line_split[args['ea_col']]
        if 'oa_col' in args and args['oa_col'] is not None:
            row['oa'] = line_split[args['oa_col']]
        if 'eaf_col' in args and args['eaf_col'] is not None:
            row['eaf'] = line_split[args['eaf_col']]
        if 'beta_col' in args and args['beta_col'] is not None:
            row['beta'] = line_split[args['beta_col']]
        if 'se_col' in args and args['se_col'] is not None:
            row['se'] = line_split[args['se_col']]
        if 'pval_col' in args and args['pval_col'] is not None:
            row['pval'] = line_split[args['pval_col']]
        if 'ncontrol_col' in args and args['ncontrol_col'] is not None:
            row['ncontrol'] = line_split[args['ncontrol_col']]
        if 'ncase_col' in args and args['ncase_col'] is not None:
            row['ncase'] = line_split[args['ncase_col']]

        # check row - raises validation exception if invalid
        schema = GwasRowSchema()
        schema.load(row)

    @staticmethod
    def __convert_index(val):
        try:
            return val - 1
        except TypeError:
            return val

    @api.expect(parser)
    def post(self):
        args = self.parser.parse_args()

        # create job identifier
        job_id = str(uuid.uuid1())
        logging.info("Starting job {}".format(job_id))

        # convert to 0-based indexing
        args['chr_col'] = Upload.__convert_index(args['chr_col'])
        args['pos_col'] = Upload.__convert_index(args['pos_col'])
        args['ea_col'] = Upload.__convert_index(args['ea_col'])
        args['oa_col'] = Upload.__convert_index(args['oa_col'])
        args['beta_col'] = Upload.__convert_index(args['beta_col'])
        args['se_col'] = Upload.__convert_index(args['se_col'])
        args['pval_col'] = Upload.__convert_index(args['pval_col'])
        args['ncase_col'] = Upload.__convert_index(args['ncase_col'])
        args['snp_col'] = Upload.__convert_index(args['snp_col'])
        args['eaf_col'] = Upload.__convert_index(args['eaf_col'])
        args['imp_z_col'] = Upload.__convert_index(args['imp_z_col'])
        args['imp_info_col'] = Upload.__convert_index(args['imp_info_col'])
        args['ncontrol_col'] = Upload.__convert_index(args['ncontrol_col'])

        # fix delim
        if args['delimiter'] == "comma":
            args['delimiter'] = ","
        elif args['delimiter'] == "tab":
            args['delimiter'] = "\t"
        elif args['delimiter'] == "space":
            args['delimiter'] = " "

        # convert text to bool
        args['header'] = (args['header'] == "True")
        args['gzipped'] = (args['gzipped'] == "True")

        # create job directory
        job_dir = os.path.join(Globals.UPLOAD_FOLDER, job_id)
        logging.info("Creating job directory: {}".format(job_dir))
        os.mkdir(job_dir)

        # upload file
        if args['gzipped']:
            output_filename = '{}.txt.gz'.format(job_id)
            output_path = os.path.join(job_dir, output_filename)

            logging.info("Saving to {}".format(output_path))
            args['gwas_file'].save(output_path)
            f = gzip.open(output_path, 'rt')
        else:
            output_filename = '{}.txt'.format(job_id)
            output_path = os.path.join(job_dir, output_filename)

            logging.info("Saving to {}".format(output_path))
            args['gwas_file'].save(output_path)
            f = open(output_path, 'r')

        # check file is valid
        if args['header']:
            logging.info("Skipping header")
            f.readline()

        try:
            logging.info("Checking file format meets specification")
            n = 0
            for line in f:
                n += 1
                if n > 1000:
                    break
                Upload.validate_row_with_schema(line.strip().split(args['delimiter']), args)
            f.close()
        except OSError as e:
            logging.error("Could not read file: {}".format(e))
            return {'message': 'Could not read file. Check encoding'}, 400
        except marshmallow.exceptions.ValidationError as e:
            logging.error("Could not read file: {}".format(e))
            return {'message': 'The file format was invalid {}'.format(e)}, 400
        except IndexError as e:
            logging.error("Could not read file: {}".format(e))
            return {'message': 'Check column numbers and separator: {}'.format(e)}, 400

        # set WDL params
        wdl = dict()

        wdl['gwas2vcf.JobId'] = job_id
        wdl['gwas2vcf.SumStatsFilename'] = output_filename

        if 'cohort_cases' in args and args['cohort_cases'] is not None:
            wdl['gwas2vcf.Cases'] = args['cohort_cases']

        if 'cohort_controls' in args and args['cohort_controls'] is not None:
            wdl['gwas2vcf.Controls'] = args['cohort_controls']

        wdl['gwas2vcf.RefGenomeFile'] = Globals.RefGenomeFile
        wdl['gwas2vcf.RefGenomeFileIdx'] = Globals.RefGenomeFileIdx
        wdl['gwas2vcf.DbSnpVcfFile'] = Globals.DbSnpVcfFile
        wdl['gwas2vcf.DbSnpVcfFileIdx'] = Globals.DbSnpVcfFileIdx
        wdl['gwas2vcf.AfVcfFile'] = Globals.AfVcfFile
        wdl['gwas2vcf.AfVcfFileIdx'] = Globals.AfVcfFileIdx

        # write out params for WDL
        logging.info("Writing out WDL parameters")
        with open(os.path.join(job_dir, 'wdl.json'), 'w') as f:
            json.dump(wdl, f)

        # write out params for gwas2vcf
        logging.info("Writing out pipeline parameters")

        # drop None values
        j = dict()
        for k in args:
            if args[k] is not None:
                j[k] = args[k]

        # drop non-gwas2vcf args & non-serializable
        del j['gwas_file']
        del j['gzipped']

        with open(os.path.join(job_dir, 'upload.json'), 'w') as f:
            json.dump(j, f)

        # add to workflow queue
        logging.info("Send POST request to cromwell for analysis")
        r = requests.post(Globals.CROMWELL_URL + "/api/workflows/v1",
                          files={'workflowSource': open(Globals.QC_WDL_PATH, 'rb'),
                                 'workflowInputs': open(os.path.join(job_dir, 'wdl.json'), 'rb')})

        assert r.status_code == 201
        assert r.json()['status'] == "Submitted"

        return {'job': job_id}, 201
