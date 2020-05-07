import logging
import os
from os import path as op
import werkzeug
# https://github.com/noirbizarre/flask-restplus/issues/777
werkzeug.cached_property = werkzeug.utils.cached_property


def init_logger(level=logging.DEBUG):
    """Initializes the logger"""
    logger = logging.getLogger(__name__)
    stream = logging.StreamHandler()
    logfile = logging.FileHandler(op.join(os.sep, "tmp", "flask_app.log"))
    stream_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logfile_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream.setFormatter(stream_format)
    logfile.setFormatter(logfile_format)
    stream.setLevel(level)
    logfile.setLevel(level)
    logger.addHandler(stream)
    logger.addHandler(logfile)
    return logger


class PowerPlantConfigurationError(ValueError):
    pass