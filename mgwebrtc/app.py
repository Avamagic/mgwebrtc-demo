from flask import Flask
from gevent import monkey; monkey.patch_all()
from .configs import DevConfig
from .frontend import frontend

# For import *
__all__ = ['create_app']

DEFAULT_BLUEPRINTS = (
    frontend,
    )

def create_app(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = DevConfig.PROJECT
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name)
    configure_app(app, config)
    configure_hook(app)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_template_filters(app)

    return app

def configure_app(app, config):
    """Configure app from object, parameter and env."""

    app.config.from_object(DevConfig)
    if config is not None:
        app.config.from_object(config)
    # Override setting by env var without touching codes.
    app.config.from_envvar('%s_APP_CONFIG' % DevConfig.PROJECT.upper(), silent=True)

def configure_hook(app):
    pass

def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

def configure_extensions(app):
    pass

def configure_template_filters(app):
    @app.template_filter('iso8601')
    def iso8601_filter(value, format='%Y-%m-%dT%H:%M:%SZ'):
        return value.strftime(format)
