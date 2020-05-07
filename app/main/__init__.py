import sys
import logging
from flask import Flask
from app.main.config import config_by_name


def create_app(config_name):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)
    return app
