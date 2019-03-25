import os
import urllib.parse as urlparse

import psycopg2


def execute_select_sql(sql):
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    dbname = url.path[1:]
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port

    con = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cursor = con.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    con.close()
    return data


def execute_insert_update_sql(sql):
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    dbname = url.path[1:]
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port

    con = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cursor = con.cursor()
    cursor.execute(sql)
    con.commit()
    con.close()
