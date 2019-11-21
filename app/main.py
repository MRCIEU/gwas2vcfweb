import flask
import logging
from globals import Globals
from flask_restplus import Api
from upload import api as upload
from status import api as status

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def index():
    return flask.send_file('index.html')


app = flask.Flask(__name__)

# home page
app.add_url_rule('/', 'index', index)

# parameters
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.config['MAX_CONTENT_LENGTH'] = 7.5e+8
app.config['ERROR_404_HELP'] = False

# configure endpoints
api = Api(version=Globals.VERSION, title='Convert GWAS to VCF format',
          description='A RESTful API for processing GWAS summary datasets', docExpansion='full',
          doc='/docs/')
api.add_namespace(upload)
api.add_namespace(status)
api.init_app(app)

if __name__ == "__main__":
    logging.info("Starting server")
    app.run(host='0.0.0.0', port=80)
