import json
import calendar
from datetime import datetime
from redis import StrictRedis, WatchError

redis = StrictRedis()

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
