import psycopg2
import redis

from functional.testdata import Config


def clear_db(config: Config):
    sql = '''
    TRUNCATE TABLE users CASCADE;
    '''

    connection = psycopg2.connect(
        **{
            'dbname': 'auth',
            'user': config.postgres_user,
            'password': config.postgres_password,
            'host': config.postgres_host,
            'port': config.postgres_port
        }
    )

    with connection.cursor() as cur:
        cur.execute(sql)
        connection.commit()


def clear_redis_request_limit(config: Config):
    r = redis.Redis(host=config.redis_host, port=config.redis_port)
    pattern = f'request:*'
    keys = r.keys(pattern)
    if keys:
        r.delete(*keys)
