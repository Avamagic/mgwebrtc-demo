from datetime import datetime
import calendar
import json
from flask import render_template, redirect, url_for, request, Response
from flask.ext.wtf import Form, TextField, validators
from redis import StrictRedis, WatchError
from mgwebrtc import app

redis = StrictRedis()

@app.template_filter('iso8601')
def iso8601_filter(value, format='%Y-%m-%dT%H:%M:%SZ'):
    return value.strftime(format)

class RoomForm(Form):
    name = TextField('Name', [validators.Required()])

def create_or_get_room(name):
    key = u'room:name-to-id:{}'.format(name)
    room_id = redis.get(key)
    if room_id:
        return room_id

    # create room
    created_at = calendar.timegm(datetime.utcnow().utctimetuple())
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
        rooms = [json.loads(info) for info in rooms]
        for room in rooms:
            room['created_at'] = datetime.utcfromtimestamp(room['created_at'])
    return render_template('index.html', form=form, rooms=rooms)

@app.route('/room/<room_id>')
def room(room_id):
    room_key = 'room:info:{}'.format(room_id)
    if not redis.exists(room_key):
        return render_template('room_not_exists.html')
    room_info_key = 'room:info:{}'.format(room_id)
    room_info = json.loads(redis.get(room_info_key))
    room_info['created_at'] = datetime.utcfromtimestamp(room_info['created_at'])
    return render_template('room.html', room_id=room_id, room_info=room_info)

@app.route('/events')
def events():
    return ''

@app.route('/about')
def about():
    return render_template('about.html')

def event_stream(channel):
    pubsub = redis.pubsub()
    pubsub.subscribe('room:channel:{}'.format(channel))
    for message in pubsub.listen():
        yield 'data: %s\n\n' % message['data']

@app.route('/pub/<channel>', methods=['POST',])
def pub(channel):
    redis.publish('room:channel:{}'.format(channel), request.form['message'])
    return Response(json.dumps({'status': 'ok'}), mimetype='application/json')

@app.route('/sub/<channel>')
def sub(channel):
    return Response(event_stream(channel), mimetype='text/event-stream')
