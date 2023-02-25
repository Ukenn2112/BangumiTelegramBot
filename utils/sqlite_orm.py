import datetime
import sqlite3
from typing import Union


class SQLite:
    def __init__(self):
        self.conn = sqlite3.connect("data/bot.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_users_db(self) -> None:
        """创建用户数据库"""
        self.cursor.execute("""create table if not exists
            user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE,
            bgm_id INTEGER,
            access_token VARCHAR(128),
            refresh_token VARCHAR(128),
            cookie VARCHAR(128),
            expiry_time TIMESTAMP,
            create_time TIMESTAMP,
            update_time TIMESTAMP)
            """
        )
        self.conn.commit()

    def insert_user_data(self, tg_id: int, bgm_id: int, access_token: str, refresh_token: str, cookie: str = None) -> None:
        """插入用户数据"""
        now_time = datetime.datetime.now().timestamp() // 1000
        expiry_time = (datetime.datetime.now() + datetime.timedelta(days=7)).timestamp() // 1000
        self.cursor.execute(
            "INSERT INTO user (tg_id, bgm_id, access_token, refresh_token, cookie, expiry_time, create_time, update_time) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (tg_id, bgm_id, access_token, refresh_token, cookie, expiry_time, now_time, now_time))
        self.conn.commit()

    def inquiry_user_data(self, tg_id) -> Union[tuple, None]:
        """查询用户数据
        :return: (0 tg_id, 1 bgm_id, 2 access_token, 3 refresh_token, 4 cookie, 5 expiry_time)"""
        data = self.cursor.execute("SELECT tg_id, bgm_id, access_token, refresh_token, cookie, expiry_time FROM user WHERE tg_id=?", (tg_id,))
        return data.fetchone()
    
    def update_user_data(self, tg_id: int, access_token: str = None, refresh_token: str = None, cookie: str = None) -> None:
        """更新用户数据"""
        now_time = datetime.datetime.now().timestamp() // 1000
        execute = "UPDATE user SET "
        if access_token and refresh_token:
            expiry_time = (datetime.datetime.now() + datetime.timedelta(days=7)).timestamp() // 1000
            execute += f"access_token='{access_token}', refresh_token='{refresh_token}', expiry_time={expiry_time}"
        if cookie:
            execute += f", cookie='{cookie}'"
        self.cursor.execute(execute + ", update_time=? WHERE tg_id=?", (now_time, tg_id))
        self.conn.commit()
    
    def delete_user_data(self, tg_id: int) -> None:
        """删除用户数据"""
        self.cursor.execute("DELETE FROM user WHERE tg_id=?", (tg_id,))
        self.conn.commit()
    
    def create_subscribe_db(self) -> None:
        """创建订阅数据库"""
        self.cursor.execute("""create table if not exists
            sub(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER,
            user_id INTEGER,
            subject_id INTEGER)
            """)
        self.conn.commit()

    def insert_subscribe_data(self, tg_id: int, bgm_id: int, subject_id: int) -> None:
        """插入订阅数据"""
        self.cursor.execute("INSERT INTO sub (tg_id, user_id, subject_id) VALUES (?, ?, ?)", (tg_id, bgm_id, subject_id))
        self.conn.commit()
    
    def delete_subscribe_data(self, subject_id: int, tg_id: int = None, bgm_id: int = None) -> None:
        """删除订阅数据"""
        self.cursor.execute("DELETE FROM sub WHERE (tg_id=? OR user_id=?) AND subject_id=?", (tg_id, bgm_id, subject_id))
        self.conn.commit()
    
    def inquiry_subscribe_data(self, subject_id: int) -> list:
        """查询 subject_id 的订阅 tg_id"""
        data = self.cursor.execute("SELECT tg_id FROM sub WHERE subject_id=?", (subject_id,)).fetchall()
        if data:
            return [i[0] for i in data]
        else:
            return []
    
    def check_subscribe(self, subject_id: int, tg_id: int = None, bgm_id: int = None) -> bool:
        """查询用户是否已订阅"""
        data = self.cursor.execute(
            "SELECT * FROM sub WHERE (tg_id=? OR user_id=?) AND subject_id=?",
            (tg_id, bgm_id, subject_id))
        return bool(data.fetchone())
    
    def close(self):
        self.conn.close()