import redis
from tests.functional.testdata.config import get_config
from time import sleep


def wait_for_redis():
    config = get_config()

    r = redis.Redis(host=config.redis_host, port=config.redis_port)

    while True:
        try:
            if r.ping() == 'PONG':
                break
        except Exception as e:
            print('Waiting for redis....')
            sleep(1)
        else:
            break


if __name__ == '__main__':
    wait_for_redis()
