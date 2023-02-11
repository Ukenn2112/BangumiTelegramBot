import sqlite3


class SQLite:
    def __init__(self):
        self.conn = sqlite3.connect("data/sqldata.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_users_db(self):
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
    
    def create_subscribe_db(self):
        """创建订阅数据库"""
        self.cursor.execute("""create table if not exists
            sub(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER,
            user_id INTEGER,
            subject_id INTEGER)
            """)
        self.conn.commit()
    
    def close(self):
        self.conn.close()