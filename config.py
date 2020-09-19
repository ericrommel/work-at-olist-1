class Config(object):
    """
    Common configurations
    """

    # Flask settings
    DEBUG = True
    TESTING = False


class DevelopmentConfig(Config):
    """
    Development configurations
    """


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False


class TestingConfig(Config):
    """
    Testing configurations
    """

    TESTING = True


app_config = {"development": DevelopmentConfig, "production": ProductionConfig, "testing": TestingConfig}
