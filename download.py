from globals import Globals
from flask_restplus import Api, Resource, Namespace
from flask import send_from_directory

api = Namespace('vcf', description="Process GWAS VCF files")


# todo error handling of missing or unprocessed files
@api.route('/download/<job_id>')
@api.doc(description="Download GWAS VCF file")
class Download(Resource):
    def get(self, job_id):
        return send_from_directory(directory=Globals.UPLOAD_FOLDER, filename="{}.vcf".format(job_id))
