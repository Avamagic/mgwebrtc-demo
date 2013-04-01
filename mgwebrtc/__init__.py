from flask import Flask

app = Flask(__name__)
app.config.update(
    DEBUG = True,
    TESTING = False,
    SECRET_KEY = "debugging key",
)
app.config.from_pyfile('custom.cfg', True)

import ui
