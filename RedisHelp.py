import os
import json
import redis
import hashlib
import threading

'''
 redis 类 
'''


class RedisHelp(object):
    _ins_lock = threading.Lock()
    _ins = {}

    def __new__(cls, *args, **kwargs):
        cls.instance(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.instance(*args, **kwargs)

    @classmethod
    def instance(cls, *args, **kwargs):
        with RedisHelp._ins_lock:
            if len(args) != 0:
                keys = ['host', 'port', 'db']
                count = len(keys)
                for i, val in enumerate(args):
                    if i < count and val is not None:
                        kwargs[keys[i]] = val
                    if i >= count:
                        break
            id_key = RedisHelp.__args_id(kwargs)
            if RedisHelp._ins is not None and RedisHelp._ins.get(id_key, False):
                return RedisHelp._ins.get(id_key)
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port')
            db = kwargs.get('db', 1)
            RedisHelp._ins[id_key] = RedisHelp.__get_redis_connection(host=host, port=port, db=db)
        return RedisHelp._ins[id_key]

    @staticmethod
    def __get_redis_connection(host='localhost', port=6379, db=1):

        if host is None or not isinstance(host, str):
            host = os.getenv('REDIS_HOST', 'localhost')
        if port is None or not isinstance(port, int) or port < 0:
            port = os.getenv('REDIS_PORT', 6379)
        if db is None or not isinstance(db, int):
            db = os.getenv('REDIS_DB', 1)
        pool = redis.ConnectionPool(host=host, port=port, db=db)
        client = redis.Redis(connection_pool=pool)
        return client

    @staticmethod
    def __args_id(args=None):
        md5 = hashlib.md5()
        if args is None:
            return md5.update('None').hexdigest()
        if isinstance(args, dict) or isinstance(args, object):
            return md5.update(json.dumps(args)).hexdigest()
