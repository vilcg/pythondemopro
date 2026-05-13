# db.py
import pymysql
from contextlib import contextmanager

class Database:
    def __init__(self, host='localhost', port=3306, user='root',
                 password='123456', db='t2024', charset='utf8mb4'):
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'db': db,
            'charset': charset
        }

    def connect(self):
        """每次调用都创建全新的连接（不再缓存）"""
        return pymysql.connect(**self.config)

    @contextmanager
    def cursor(self):
        """获取游标，自动提交/回滚，使用完毕后关闭连接"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()


# if __name__ == "__main__":
#     db = Database()
#     try:
#         db.connect()
#         print("✅ 连接成功！")
#     except Exception as e:
#         print(f"❌ 连接失败：{e}")
#     finally:
#         db.close()
     


