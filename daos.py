# daos.py
"""
数据访问对象（DAO）
- 负责实体对象与数据库表之间的映射
- 提供 CRUD 操作，统一使用 JSON 序列化处理关联列表
- 所有数据库操作通过 Database 的上下文管理器执行，确保事务安全
"""

import json
from models import Student, Course, Teacher


class StudentDAO:
    """学生数据访问对象"""

    def __init__(self, db):
        self.db = db

    def get_by_id(self, student_id):
        """
        根据学号查询学生
        返回 Student 对象（courses 中存储课程ID列表），若不存在返回 None
        """
        with self.db.cursor() as cursor:
            sql = "SELECT student_id, name, courses FROM student WHERE student_id = %s"
            cursor.execute(sql, (student_id,))
            row = cursor.fetchone()
            if row:
                student = Student(row[0], row[1])
                courses_json = row[2]
                if courses_json:
                    # 数据库存储的 JSON 为课程ID列表（字符串）
                    student.courses = json.loads(courses_json)
                return student
            return None

    def save(self, student):
        """
        保存学生信息（插入或更新）
        如果 student_id 已存在则更新，否则插入新记录
        courses 字段自动序列化为 JSON 列表
        """
        with self.db.cursor() as cursor:
            # 提取课程ID列表（兼容 courses 中可能保存 Course 对象的情况）
            course_ids = []
            for c in student.courses:
                if isinstance(c, str):
                    course_ids.append(c)
                else:
                    course_ids.append(c.course_id)
            courses_json = json.dumps(course_ids, ensure_ascii=False)

            # 检查记录是否存在
            sql_check = "SELECT student_id FROM student WHERE student_id = %s"
            cursor.execute(sql_check, (student.student_id,))
            exists = cursor.fetchone()

            if exists:
                sql_update = "UPDATE student SET name = %s, courses = %s WHERE student_id = %s"
                cursor.execute(sql_update, (student.name, courses_json, student.student_id))
            else:
                sql_insert = "INSERT INTO student (student_id, name, courses) VALUES (%s, %s, %s)"
                cursor.execute(sql_insert, (student.student_id, student.name, courses_json))

    def get_all(self):
        """获取所有学生（扩展方法，供测试使用）"""
        with self.db.cursor() as cursor:
            cursor.execute("SELECT student_id, name, courses FROM student")
            rows = cursor.fetchall()
            students = []
            for row in rows:
                s = Student(row[0], row[1])
                if row[2]:
                    s.courses = json.loads(row[2])
                students.append(s)
            return students


class CourseDAO:
    """课程数据访问对象"""

    def __init__(self, db):
        self.db = db

    def get_by_id(self, course_id):
        """
        根据课程编号查询课程
        返回 Course 对象（students 中存储学生ID列表），若不存在返回 None
        """
        with self.db.cursor() as cursor:
            sql = "SELECT course_id, course_name, capacity, students, teacher_id FROM course WHERE course_id = %s"
            cursor.execute(sql, (course_id,))
            row = cursor.fetchone()
            if row:
                course = Course(row[0], row[1], row[2], teacher_id=row[4])
                students_json = row[3]
                if students_json:
                    course.students = json.loads(students_json)
                return course
            return None

    def save(self, course):
        """
        保存课程信息（插入或更新）
        """
        with self.db.cursor() as cursor:
            student_ids = []
            for s in course.students:
                if isinstance(s, str):
                    student_ids.append(s)
                else:
                    student_ids.append(s.student_id)
            students_json = json.dumps(student_ids, ensure_ascii=False)

            sql_check = "SELECT course_id FROM course WHERE course_id = %s"
            cursor.execute(sql_check, (course.course_id,))
            exists = cursor.fetchone()

            if exists:
                sql_update = ("UPDATE course SET course_name = %s, capacity = %s, "
                              "students = %s, teacher_id = %s WHERE course_id = %s")
                cursor.execute(sql_update, (course.course_name, course.capacity,
                                            students_json, course.teacher_id, course.course_id))
            else:
                sql_insert = ("INSERT INTO course (course_id, course_name, capacity, "
                              "students, teacher_id) VALUES (%s, %s, %s, %s, %s)")
                cursor.execute(sql_insert, (course.course_id, course.course_name,
                                            course.capacity, students_json, course.teacher_id))

    def get_all(self):
        """获取所有课程（扩展方法）"""
        with self.db.cursor() as cursor:
            cursor.execute("SELECT course_id, course_name, capacity, students, teacher_id FROM course")
            rows = cursor.fetchall()
            courses = []
            for row in rows:
                c = Course(row[0], row[1], row[2], teacher_id=row[4])
                if row[3]:
                    c.students = json.loads(row[3])
                courses.append(c)
            return courses


class TeacherDAO:
    """教师数据访问对象（扩展）"""

    def __init__(self, db):
        self.db = db

    def get_by_id(self, teacher_id):
        """
        根据教师编号查询教师
        返回 Teacher 对象（courses_taught 中存储课程ID列表）
        """
        with self.db.cursor() as cursor:
            sql = "SELECT teacher_id, name, courses_taught FROM teacher WHERE teacher_id = %s"
            cursor.execute(sql, (teacher_id,))
            row = cursor.fetchone()
            if row:
                teacher = Teacher(row[0], row[1])
                courses_json = row[2]
                if courses_json:
                    teacher.courses_taught = json.loads(courses_json)
                return teacher
            return None

    def save(self, teacher):
        """保存教师信息（插入或更新）"""
        with self.db.cursor() as cursor:
            course_ids = []
            for c in teacher.courses_taught:
                if isinstance(c, str):
                    course_ids.append(c)
                else:
                    course_ids.append(c.course_id)
            courses_json = json.dumps(course_ids, ensure_ascii=False)

            sql_check = "SELECT teacher_id FROM teacher WHERE teacher_id = %s"
            cursor.execute(sql_check, (teacher.person_id,))
            exists = cursor.fetchone()

            if exists:
                sql_update = "UPDATE teacher SET name = %s, courses_taught = %s WHERE teacher_id = %s"
                cursor.execute(sql_update, (teacher.name, courses_json, teacher.person_id))
            else:
                sql_insert = "INSERT INTO teacher (teacher_id, name, courses_taught) VALUES (%s, %s, %s)"
                cursor.execute(sql_insert, (teacher.person_id, teacher.name, courses_json))

    def get_all(self):
        """获取所有教师"""
        with self.db.cursor() as cursor:
            cursor.execute("SELECT teacher_id, name, courses_taught FROM teacher")
            rows = cursor.fetchall()
            teachers = []
            for row in rows:
                t = Teacher(row[0], row[1])
                if row[2]:
                    t.courses_taught = json.loads(row[2])
                teachers.append(t)
            return teachers