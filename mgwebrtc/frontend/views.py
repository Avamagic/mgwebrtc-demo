from datetime import datetime
import json
from flask import Blueprint, Response
from flask import render_template, redirect, url_for, request
from .forms import RoomForm
from .utils import redis, create_or_get_room

frontend = Blueprint('frontend', __name__,
                     template_folder='templates')

@frontend.route('/', methods=['GET', 'POST'])
def index():
    form = RoomForm()
    if form.validate_on_submit():
        room_id = create_or_get_room(form.name.data)
        return redirect(url_for('.room', room_id=room_id))

    room_keys = ['room:info:{}'.format(room_id) for room_id in redis.zrange('room:list', 0, -1)]
    if not room_keys:
        rooms = []
    else:
        rooms = redis.mget(room_keys)
        rooms = [json.loads(info) for info in rooms]
        for room in rooms:
            room['created_at'] = datetime.utcfromtimestamp(room['created_at'])
    return render_template('index.html', form=form, rooms=rooms)

@frontend.route('/room/<room_id>')
def room(room_id):
    room_key = 'room:info:{}'.format(room_id)
    if not redis.exists(room_key):
        return render_template('room_not_exists.html')
    room_info_key = 'room:info:{}'.format(room_id)
    room_info = json.loads(redis.get(room_info_key))
    room_info['created_at'] = datetime.utcfromtimestamp(room_info['created_at'])
    return render_template('room.html', room_id=room_id, room_info=room_info)

@frontend.route('/about')
def about():
    return render_template('about.html')

def event_stream(channel):
    pubsub = redis.pubsub()
    pubsub.subscribe('room:channel:{}'.format(channel))
    for message in pubsub.listen():
        yield 'data: %s\n\n' % message['data']

@frontend.route('/pub/<channel>', methods=['POST',])
def pub(channel):
    redis.publish('room:channel:{}'.format(channel), request.form['message'])
    return Response(json.dumps({'status': 'ok'}), mimetype='application/json')

@frontend.route('/sub/<channel>')
def sub(channel):
    return Response(event_stream(channel), mimetype='text/event-stream')
