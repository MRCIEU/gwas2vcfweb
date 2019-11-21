from globals import Globals
from flask_restplus import Resource, Namespace
from flask import send_file, jsonify
import os
from flask import abort
import logging

api = Namespace('vcf', description="Retrieve GWAS VCF files")


@api.route('/download')
@api.doc(description="Download GWAS VCF file")
@api.header('Content-Type', 'application/octet-stream')
class Download(Resource):
    parser = api.parser()
    parser.add_argument('job_id', type=str, required=True, help="Job identifier")

    @api.expect(parser)
    def get(self):
        args = self.parser.parse_args()

        job_dir = os.path.join(Globals.UPLOAD_FOLDER, args['job_id'])
        logging.info("Looking for data in: {}".format(job_dir))
        filename = "{}.vcf.gz".format(args['job_id'])
        logging.info("Looking for completed filename in: {}".format(filename))

        # check job dir is valid
        if not os.path.isdir(job_dir):
            logging.error("Directory does not exist, check UUID")
            abort(404, "Job {} does not exist on server".format(args['job_id']))

        # check output file is ready for download
        if not os.path.exists(os.path.join(job_dir, filename)):
            logging.info("No outputs available. Result are processing or failed")
            return jsonify(message="Job {} is not complete. Please check back later".format(args['job_id']))

        return send_file(os.path.join(job_dir, filename), attachment_filename=filename, as_attachment=True)
