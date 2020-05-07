import os
import logging
from flask import request, jsonify
from app.main import create_app
from app.main.utils.general_utils import init_logger
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from flask_restplus import Api
from flask import Blueprint
from app.main.controller.production_plan_controller import PowerPlantResource, powerplant_namespace

init_logger(level=logging.DEBUG)
app = create_app(os.getenv('FLASK_ENV') or 'development')
app.app_context().push()
blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='Web App to return power plant loads',
          version='1.0',
          description='Power Plant Load'
          )
api.add_namespace(powerplant_namespace)

app.register_blueprint(blueprint)

app.app_context().push()
app.run(host="127.0.0.1", port=5000, debug=True)
