import logging
from app.main.service import load_calculations
from flask_restplus import Resource, Namespace
from app.main.controller.input_validation import PowerPlantLoadSchema
from webargs.flaskparser import use_args, parser, use_kwargs, abort

powerplant_namespace = Namespace('powerplant', description='Power plant loading related operations')
logger = logging.getLogger(__name__)


@powerplant_namespace.route("/")
class PowerPlantResource(Resource):
    @use_kwargs(PowerPlantLoadSchema, location="json")
    def post(self, input_args):
        return load_calculations.load_distributor(input_args)

