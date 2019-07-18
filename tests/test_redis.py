import os
import dotenv
from RedisHelp import RedisTool as Redis


def curr():
    return os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    env_file = os.path.dirname(curr()) + "/config/.env"
    dotenv.load_dotenv(env_file)
    red = Redis.instance()
    red2 = Redis.instance()
    print(red == red2)
    # red.set('test_python', 123)
    val = red.get('test_python')
    if val is not None:
        print(val.decode('utf-8'))
    ret = red.setex(name='test_python_expire', value='hello world', time=60)
    print(ret)
    print(red.get('test_python_expire'))
    red1 = Redis.instance(db=1)
    print(red1.delete('test_python'))
