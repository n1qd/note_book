import pymysql
from private import db_config

def create_database():
    conn = pymysql.connect(**db_config)
    with conn.cursor() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title TEXT NOT NULL,
                content LONGTEXT NOT NULL,
                category TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
    conn.close()
