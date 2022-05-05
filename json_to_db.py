"""
将 bgm_data.json 转换 bot.db

"""
import datetime
import json
import sqlite3
import time

sql_con = sqlite3.connect(
    "bot.db",
    check_same_thread=False,
    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
)


def create_sql():
    """创建数据库"""

    sql_con.execute(
        """create table if not exists
        user(
        id integer primary key AUTOINCREMENT,
        tg_id integer,
        bgm_id integer,
        access_token varchar(128),
        refresh_token varchar(128),
        cookie varchar(128),
        expiry_time timestamp,
        create_time timestamp,
        update_time timestamp)
        """
    )

    sql_con.execute("""create unique index if not exists tg_id_index on user (tg_id)""")


def add_data():
    """转换数据库"""
    with open('bgm_data.json', encoding='UTF-8') as f:
        data_seek = json.loads(f.read())
    for data in data_seek:
        tg_id = data['tg_user_id']
        bgm_id = data['data']['user_id']
        access_token = data['data']['access_token']
        refresh_token = data['data']['refresh_token']
        cookie = data['data'].get('cookie')
        expiry_time = int(time.mktime(time.strptime(data['expiry_time'], "%Y%m%d"))) // 1000
        sql_con.execute(
            "insert into user(tg_id,bgm_id,access_token,refresh_token,cookie,expiry_time,create_time) "
            "values(?,?,?,?,?,?,?)",
            (
                tg_id,
                bgm_id,
                access_token,
                refresh_token,
                cookie,
                expiry_time,
                datetime.datetime.now().timestamp() // 1000,
            ),
        )
        sql_con.commit()
    return print("转换成功")


create_sql()
add_data()
