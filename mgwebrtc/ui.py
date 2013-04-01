from flask import render_template
from mgwebrtc import app

@app.route('/')
def index():
    return render_template('index.html')
