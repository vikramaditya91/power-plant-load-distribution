import logging
from app.main.service import load_calculations
from flask_restplus import Resource, Namespace
from app.main.controller.input_validation import PowerPlantLoadSchema
from webargs.flaskparser import use_args, parser

powerplant_namespace = Namespace('powerplant', description='Power plant loading related operations')
logger = logging.getLogger(__name__)


@powerplant_namespace.route("/")
class PowerPlantResource(Resource):
    @use_args(PowerPlantLoadSchema, location="json")
    def post(self, input_args):
        distributed_load_raw = load_calculations.load_distributor(input_args)
        sanitized_load_distib = load_calculations.sanitize_load(distributed_load_raw)
        return input_args


@parser.error_handler
def handle_request_parsing_error(err, req, schema, *, error_status_code, error_headers):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    logger.warning(req)
    logger.debug(schema)
    logger.debug(err)
    logger.debug(error_status_code)
    logger.debug(error_headers)
