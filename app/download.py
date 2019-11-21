from globals import Globals
from flask_restplus import Resource, Namespace
from flask import send_file
import os
import logging

api = Namespace('vcf', description="Download VCF file")


@api.route('/download')
@api.doc(description="Download of VCF file")
class Download(Resource):
    parser = api.parser()
    parser.add_argument('job_id', type=str, required=True, help="Job identifier")
    parser.add_argument('file_type', type=str, choices=("vcf", "tbi"), required=True, help="File type")

    @api.expect(parser)
    def get(self):
        args = self.parser.parse_args()

        job_dir = os.path.join(Globals.UPLOAD_FOLDER, args['job_id'])
        logging.info("Looking for data in: {}".format(job_dir))
        vcf = "{}.vcf.gz".format(args['job_id'])
        tbi = "{}.vcf.gz.tbi".format(args['job_id'])

        if args['file_type'] == "vcf":
            if not os.path.exists(os.path.join(job_dir, vcf)):
                logging.error("File does not exist: {}".format(os.path.join(job_dir, vcf)))
                return "File does not exist", 404
            logging.info("Returning file: {}".format(os.path.join(job_dir, vcf)))
            return send_file(os.path.join(job_dir, vcf), as_attachment=True)

        if args['file_type'] == "tbi":
            if not os.path.exists(os.path.join(job_dir, tbi)):
                logging.error("File does not exist: {}".format(os.path.join(job_dir, tbi)))
                return "File does not exist", 404
            logging.info("Returning file: {}".format(os.path.join(job_dir, tbi)))
            return send_file(os.path.join(job_dir, tbi), as_attachment=True)
