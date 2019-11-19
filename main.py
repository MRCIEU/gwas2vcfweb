import flask
from api import api
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def index():
    return flask.render_template('index.html')


app = flask.Flask(__name__)

app.add_url_rule('/', 'index', index)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.config['MAX_CONTENT_LENGTH'] = 7.5e+8
api.init_app(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
