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

api = Namespace('txt', description="Convert GWAS summary stats files")


@api.route('/upload')
@api.doc(description="Upload GWAS summary stats file")
class Upload(Resource):
    parser = api.parser()
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
    parser.add_argument('gwas_file', location='files', type=FileStorage, required=True,
                        help="Path to GWAS summary stats text file for upload")
    parser.add_argument('gzipped', type=str, required=True, help="Is the file compressed with gzip?",
                        choices=('True', 'False'))
    parser.add_argument('build', type=str, choices=('GRCh37',), required=True,
                        help='Genome build used to perform the GWAS study.')
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
        args['job_id'] = str(uuid.uuid1())

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

        # create job directory
        job_dir = os.path.join(Globals.UPLOAD_FOLDER, args['job_id'])
        os.mkdir(job_dir)

        # upload file
        if args['gzipped'] == 'True':
            output_path = os.path.join(job_dir, '{}.txt.gz'.format(args['job_id']))
            args['gwas_file'].save(output_path)
            f = gzip.open(output_path, 'rt')
        else:
            output_path = os.path.join(job_dir, '{}.txt'.format(args['job_id']))
            args['gwas_file'].save(output_path)
            f = open(output_path, 'r')

        # check file is valid
        if args['header'] == 'True':
            f.readline()

        try:
            n = 0
            for line in f:
                n += 1
                if n > 1000:
                    break
                Upload.validate_row_with_schema(line.strip().split(args['delimiter']), args)
            f.close()
        except OSError:
            return {'message': 'Could not read file. Check encoding'}, 400
        except marshmallow.exceptions.ValidationError as e:
            return {'message': 'The file format was invalid {}'.format(e)}, 400
        except IndexError as e:
            return {'message': 'Check column numbers and separator: {}'.format(e)}, 400

        # drop non-serializable
        del args['gwas_file']

        with open(os.path.join(job_dir, '{}.json'.format(args['job_id'])), 'w') as f:
            json.dump(args, f)

        # add to workflow queue
        r = requests.post(Globals.CROMWELL_URL + "/api/workflows/v1",
                          files={'workflowSource': open(Globals.QC_WDL_PATH, 'rb'),
                                 'workflowInputs': open(
                                     os.path.join(job_dir, '{}.json'.format(args['job_id'])), 'rb')})
        assert r.status_code == 201
        assert r.json()['status'] == "Submitted"

        return {'job': args['job_id']}, 201
