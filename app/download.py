from globals import Globals
from flask_restplus import Resource, Namespace
from flask import send_from_directory
import os
from flask import abort

api = Namespace('vcf', description="Retrieve GWAS VCF files")


@api.route('/download')
@api.doc(description="Download GWAS VCF file")
class Download(Resource):
    parser = api.parser()
    parser.add_argument('job_id', type=str, required=True, help="Job identifier")

    @api.expect(parser)
    def get(self):
        args = self.parser.parse_args()

        job_dir = os.path.join(Globals.UPLOAD_FOLDER, args['job_id'])
        filename = "{}.vcf.gz".format(args['job_id'])

        # check job dir is valid
        if not os.path.isdir(job_dir):
            abort(404, "Job {} does not exist on server".format(args['job_id']))

        # check output file is ready for download
        if not os.path.exists(os.path.join(job_dir, filename)):
            abort(102, "Job {} is not complete. Check back later".format(args['job_id']))

        return send_from_directory(directory=job_dir, filename=filename)
