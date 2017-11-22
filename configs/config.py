import os
root_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'peb_dns_author_lijiajia'
    ROOT_DIR = root_dir

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'default': ProductionConfig
}

config_pyfiles = {
    'dev': 'configs/dev.cfg',
    'prod': 'configs/prod.cfg',
    'default': 'configs/prod.cfg'
}

