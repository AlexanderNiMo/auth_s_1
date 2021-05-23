import psycopg2
import redis


def clear_db():
    sql = '''
    TRUNCATE TABLE users CASCADE;
    '''

    connection = psycopg2.connect(
        **{
            'dbname': 'auth',
            'user': 'postgres',
            'password': 'qwerty',
            'host': 'localhost',
            'port': 5432
        }
    )

    with connection.cursor() as cur:
        cur.execute(sql)
        connection.commit()


def clear_redis_request_limit():
    r = redis.Redis(host='localhost', port=6379)
    pattern = f'request:*'
    keys = r.keys(pattern)
    r.delete(*keys)
