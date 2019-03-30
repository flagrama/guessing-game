import os
import urllib.parse as urlparse

import psycopg2

SQL_PARTICIPANT_INSERT = "INSERT INTO participants " \
                         "(uuid, name, twitch_id, points, current_points, user_id) " \
                         "VALUES ('{}','{}', {}, 0, 0, {})"
SQL_RESULT_INSERT = "INSERT INTO results " \
                    "(uuid, datetime, results, user_id)" \
                    "VALUES ('{}', '{}', {}, {})"
SQL_GET_BOT_ENABLED_ROOMS = "SELECT {} FROM {} WHERE {}".format(
    'twitch_login_name',
    'users',
    'bot_enabled IS TRUE'
)
SQL_CHANNEL_USER_ID = "SELECT {} FROM {} WHERE {}".format(
    'id',
    'users',
    'users.twitch_id={}'
)
SQL_CHANNEL_USER_ID_BY_LOGIN = "SELECT {} FROM {} WHERE {}".format(
    'id',
    'users',
    "users.twitch_login_name='{}'"
)
SQL_CURRENT_USER_VARIATIONS = "SELECT {} FROM {} JOIN {} ON {} WHERE {}".format(
    'variations',
    'guessables',
    'users',
    'guessables.user_id=users.id',
    'users.twitch_id={}'
)
SQL_GET_POINTS = "SELECT {} FROM {} JOIN {} ON {} WHERE {} AND {}".format(
    '{}',
    'participants',
    'users',
    'participants.user_id=users.id',
    'users.twitch_id={}',
    'participants.twitch_id={}'
)
SQL_GET_PARTICIPANT = "SELECT {} FROM {} JOIN {} ON {} WHERE {} AND {}".format(
    '*',
    'participants',
    'users',
    'participants.user_id=users.id',
    'users.twitch_id={}',
    'participants.twitch_id={}'
)
SQL_GET_PARTICIPANT_TWITCH_LOGIN = "SELECT {} FROM {} JOIN {} ON {} WHERE {} AND {}".format(
    '{}',
    'participants',
    'users',
    'participants.user_id=users.id',
    "users.twitch_login_name='{}'",
    'participants.twitch_id={}'
)
SQL_GET_VARIATIONS_GUESSING_GAME = "SELECT {} FROM {} JOIN {} ON {} WHERE {}".format(
    'variations',
    'guessables',
    'users',
    'guessables.user_id=users.id',
    "users.twitch_login_name='{}'"
)
SQL_UPDATE_PARTICIPANT_POINTS = "UPDATE {} SET {} FROM {} WHERE {} AND {} AND {}".format(
    'participants',
    'points={}',
    'users',
    'participants.user_id=users.id',
    "users.twitch_login_name='{}'",
    'participants.twitch_id={}'
)


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
