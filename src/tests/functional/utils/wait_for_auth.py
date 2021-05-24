import requests
from time import sleep

from tests.functional.testdata.config import get_config


def wait_for_api():
    config = get_config()
    while not get_status(config):
        sleep(1)


def get_status(config):
    health_url = f'http://{config.auth_host}:{config.auth_port}/api/health'
    try:
        result = requests.get(health_url)
        if not result.ok:
            return False
        data = await result.json()
        return data.get('status', False)
    except requests.HTTPError as err:
        return False


if __name__ == '__main__':
    wait_for_api()