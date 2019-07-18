import os
import json
import redis
import hashlib
import threading

'''
 redis 类 
'''


class RedisTool(object):
    _ins_lock = threading.Lock()
    _ins = {}

    def __new__(cls, *args, **kwargs):
        cls.instance(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.instance(*args, **kwargs)

    '''
    获取连接实例
    @:param host :str
    @:param port :int
    @:param db : int
    @:return redis.Redis
    '''

    @classmethod
    def instance(cls, *args, **kwargs):
        with RedisTool._ins_lock:
            if len(args) != 0:
                keys = ['host', 'port', 'db']
                count = len(keys)
                for i, val in enumerate(args):
                    if i < count and val is not None:
                        kwargs[keys[i]] = val
                    if i >= count:
                        break
            id_key = RedisTool.__args_id(kwargs)
            if RedisTool._ins is not None and RedisTool._ins.get(id_key, False):
                return RedisTool._ins.get(id_key)
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port')
            db = kwargs.get('db', -1)
            RedisTool._ins[id_key] = RedisTool.__get_redis_connection(host=host, port=port, db=db)
        return RedisTool._ins[id_key]

    '''
    获取连接实例
    @:param host :str
    @:param port :int
    @:param db : int
    @:return redis.Redis
    '''

    @staticmethod
    def __get_redis_connection(host='localhost', port=6379, db=-1):

        if host is None or not isinstance(host, str):
            host = os.getenv('REDIS_HOST', 'localhost')
        if port is None or not isinstance(port, int) or port < 0:
            port = int(os.getenv('REDIS_PORT', 6379))
        if db is None or not isinstance(db, int) or db < 0:
            db = int(os.getenv('REDIS_DB', 1))
        pool = redis.ConnectionPool(host=host, port=port, db=db)
        client = redis.Redis(connection_pool=pool)
        return client

    @staticmethod
    def __args_id(args=None):
        md5 = hashlib.md5()
        if args is None:
            return md5.update('None').hexdigest()
        if isinstance(args, dict) or isinstance(args, object):
            val = str(json.dumps(args)).encode('utf-8')
            md5.update(val)
            return md5.hexdigest()

    @staticmethod
    def md5(data):
        md5 = hashlib.md5()
        if data is None:
            data = str(None).encode('utf-8')
        if isinstance(data, dict) or isinstance(data, object):
            data = str(json.dumps(data)).encode('utf-8')
        else:
            data = str(data).encode('utf-8')
        md5.update(data)
        return md5.hexdigest()
