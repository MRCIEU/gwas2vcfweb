from globals import Globals
from flask_restplus import Resource, Namespace
from flask import jsonify
import os
import logging

api = Namespace('vcf', description="Status for VCF file conversion")


@api.route('/status')
@api.doc(description="Status of VCF file")
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
            return "Job {} does not exist on server".format(args['job_id']), 404

        # check output file is ready for download
        if not os.path.exists(os.path.join(job_dir, filename)):
            logging.info("No outputs available. Result are processing or failed")
            return jsonify(message="Job {} is not complete. Please check back later".format(args['job_id']))

        return jsonify(message="Job {} is complete.".format(args['job_id']),
                       vcf_uri="/data/" + args['job_id'] + "/" + filename,
                       tbi_uri="/data/" + args['job_id'] + "/" + filename + ".tbi")
