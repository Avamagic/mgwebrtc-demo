from flask import render_template
from mgwebrtc import app

@app.route('/')
def rooms():
    return render_template('rooms.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/conf')
def conf():
    return render_template('conf.html')

@app.route('/events')
def events():
    return ''
