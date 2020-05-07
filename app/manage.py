import os
from app.main import create_app
import werkzeug
# https://github.com/noirbizarre/flask-restplus/issues/777
werkzeug.cached_property = werkzeug.utils.cached_property
from flask_restplus import Api
from flask import Blueprint
from app.main.controller.production_plan_controller import powerplant_namespace

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
app.logger.debug("Starting Flask App!")
app.run(host="0.0.0.0", port=5001, debug=True)
