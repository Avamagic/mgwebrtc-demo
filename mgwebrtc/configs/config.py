import os

class BaseConfig(object):

    # Get app root path
    # ../../configs/config.py
    _basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    PROJECT = "mgwebrtc"
    DEBUG = False
    TESTING = False

    ADMINS = frozenset(['ronhuang@avamagic.com'])

    # os.urandom(24)
    SECRET_KEY = 'secret key'

class DevConfig(BaseConfig):

    DEBUG = True

class TestConfig(BaseConfig):

    TESTING = True
    CSRF_ENABLED = False
