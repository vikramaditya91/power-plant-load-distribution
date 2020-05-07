import logging
from app.main.model.power_plant import PowerPlantConfigurationError
from app.main.service import load_calculations
from flask_restplus import Resource, Namespace
from app.main.controller.input_validation import PowerPlantLoadSchema
from webargs.flaskparser import use_args, parser, abort

powerplant_namespace = Namespace('powerplant', description='Power plant loading related operations')
log = logging.getLogger('controller')


@powerplant_namespace.route("/")
class PowerPlantResource(Resource):
    @use_args(PowerPlantLoadSchema, location="json")
    def post(self, input_args):
        try:
            return load_calculations.load_distributor(input_args)
        except PowerPlantConfigurationError:
            log.warning("Impossible load requested from powerplants")
            abort(400, custom=f"Load {input_args.get('load')} cannot be distributed with the current power plants")


@parser.error_handler
def handle_parse_error(err, req, schema, *, error_status_code, error_headers):
    log.warning(f"Failed to establish schema :{schema} because {err}")
    abort(422, messages=err.messages, exc=err)

