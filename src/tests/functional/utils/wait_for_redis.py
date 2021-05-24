import requests
from tests.functional.testdata.config import get_config
from time import sleep


def wait_for_redis():
    config = get_config()

    while True:
        try:
            requests.get(f'http://{config.redis_host}:{config.redis_port}')
        except ConnectionRefusedError as e:
            print('Waiting for redis....')
            sleep(1)
        else:
            break

if __name__ == '__main__':
    wait_for_redis()