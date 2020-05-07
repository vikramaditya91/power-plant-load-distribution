import logging

logger = logging.getLogger(__name__)


class Config:
    DEBUG = True


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    logger.error("The Testing Env has not been implemented")


class ProductionConfig(Config):
    logger.error("The Production Env has not been implemented")


config_by_name = dict(
    development=DevelopmentConfig,
    test=TestingConfig,
    production=ProductionConfig
)
