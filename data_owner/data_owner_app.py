import os
from logging.config import dictConfig
from flask import Flask, jsonify
from flask_cors import CORS
from data_owner.resources import api
from data_owner.services.data_owner_service import DataOwnerService
from commons.data.data_loader import DataLoader
from data_owner.services.data_base import Database
from data_owner.config.logging_config import DEV_LOGGING_CONFIG, PROD_LOGGING_CONFIG


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


def create_app():
    # create and configure the app
    flask_app = Flask(__name__)
    if 'ENV_PROD' in os.environ and os.environ['ENV_PROD']:
        flask_app.config.from_pyfile("config/prod/app_config.py")
        dictConfig(PROD_LOGGING_CONFIG)
    else:
        dictConfig(DEV_LOGGING_CONFIG)
        flask_app.config.from_pyfile("config/dev/app_config.py")
    # ensure the instance folder exists
    try:
        os.makedirs(flask_app.instance_path)
    except OSError:
        pass
    return flask_app


# Global variables
app = create_app()
api.init_app(app)

CORS(app)
data_base = Database(app.config)
data_loader = DataLoader()
data_loader.init(app.config["DATASETS_DIR"])
data_owner_service = DataOwnerService()
data_owner_service.init(app.config)
active_encryption = app.config["ACTIVE_ENCRYPTION"]


@app.errorhandler(Exception)
def handle_error(error):
    message = [str(x) for x in error.args]
    status_code = error.status_code
    success = False
    response = {
        'success': success,
        'error': {
            'type': error.__class__.__name__,
            'message': message
        }
    }
    return jsonify(response), status_code


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify(200)
