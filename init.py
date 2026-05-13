# init_db.py
"""
自动建表并插入默认管理员
运行一次即可
"""
from db import Database

def init():
    db = Database(host='localhost', user='root', password='c7386459', db='t2024')
    db.connect()
    try:
        with db.cursor() as cursor:
            # 学生表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS student (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50),
                    student_id VARCHAR(50) UNIQUE,
                    courses JSON
                )
            """)
            # 课程表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS course (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    course_name VARCHAR(50),
                    course_id VARCHAR(50) UNIQUE,
                    capacity INT,
                    students JSON,
                    teacher_id VARCHAR(50)
                )
            """)
            # 教师表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teacher (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50),
                    teacher_id VARCHAR(50) UNIQUE,
                    courses_taught JSON
                )
            """)
            # 用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE,
                    password_hash VARCHAR(64),
                    role ENUM('admin', 'teacher', 'student')
                )
            """)
        print("数据库表创建成功")
    finally:
        db.close()

if __name__ == '__main__':
    init()