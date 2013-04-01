from datetime import datetime
import time
import json
from flask import render_template, redirect, url_for
from flask.ext.wtf import Form, TextField, validators
from redis import StrictRedis, WatchError
from mgwebrtc import app

redis = StrictRedis()

class RoomForm(Form):
    name = TextField('Name', [validators.Required()])

def create_or_get_room(name):
    key = u'room:name-to-id:{}'.format(name)
    room_id = redis.get(key)
    if room_id:
        return room_id

    # create room
    created_at = int(time.mktime(datetime.utcnow().utctimetuple()))
    with redis.pipeline() as pipe:
        while True:
            try:
                pipe.watch('room:sequence-id')
                room_id = pipe.get('room:sequence-id') or 1

                pipe.multi()

                pipe.set('room:sequence-id', int(room_id) + 1)

                pipe.set(u'room:name-to-id:{}'.format(name), room_id)
                pipe.zadd('room:list', created_at, room_id)

                info = {
                    'id': room_id,
                    'name': name,
                    'users': 0,
                    'created_at': created_at,
                }
                room_info_key = 'room:info:{}'.format(room_id)
                pipe.set(room_info_key, json.dumps(info))

                pipe.execute()
                break
            except WatchError:
                continue
    return room_id

@app.route('/', methods=['GET', 'POST'])
def index():
    form = RoomForm()
    if form.validate_on_submit():
        room_id = create_or_get_room(form.name.data)
        return redirect(url_for('room', room_id=room_id))

    room_keys = ['room:info:{}'.format(room_id) for room_id in redis.zrange('room:list', 0, -1)]
    if not room_keys:
        rooms = []
    else:
        rooms = redis.mget(room_keys)
        print [info for info in rooms]
        rooms = [json.loads(info) for info in rooms]
    return render_template('index.html', form=form, rooms=rooms)

@app.route('/room/<room_id>')
def room(room_id):
    room_key = 'room:info:{}'.format(room_id)
    if not redis.exists(room_key):
        return render_template('room_not_exists.html')
    room_info_key = 'room:info:{}'.format(room_id)
    room_info = json.loads(redis.get(room_info_key))
    return render_template('room.html', room_id=room_id, room_info=room_info)

@app.route('/events')
def events():
    return ''

@app.route('/about')
def about():
    return render_template('about.html')
