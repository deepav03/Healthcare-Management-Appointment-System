from contextlib import contextmanager

import pymysql

from utils.config_reader import config


@contextmanager
def connection():
    db = pymysql.connect(host=config.db_host, port=config.db_port, user=config.db_user, password=config.db_password, database=config.db_name, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    try:
        yield db
    finally:
        db.close()


def can_connect() -> bool:
    try:
        with connection() as db:
            with db.cursor() as cursor:
                cursor.execute("SELECT 1 AS connected")
                return cursor.fetchone()["connected"] == 1
    except pymysql.MySQLError:
        return False
