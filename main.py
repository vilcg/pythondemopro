# main.py
"""
完整测试脚本：演示学生选课、退课、教师分配等功能
运行前请确保 MySQL 服务已启动，并已创建数据库 t2024 及对应表
"""

from db import Database
from daos import StudentDAO, CourseDAO, TeacherDAO
from service import EnrollmentService, TeachingService
from models import Student, Course, Teacher


def main():
    # ---------- 1. 初始化数据库连接 ----------
    db = Database(host='localhost', user='root', password='c7386459', db='t2024')
    student_dao = StudentDAO(db)
    course_dao = CourseDAO(db)
    teacher_dao = TeacherDAO(db)

    # ---------- 2. 创建服务对象 ----------
    enroll_service = EnrollmentService(db, student_dao, course_dao)
    teach_service = TeachingService(db, teacher_dao, course_dao)

    # ---------- 3. 创建学生和课程对象（内存中） ----------
    s1 = Student('s001', '张三')
    s2 = Student('s002', '李四')
    c1 = Course('c001', 'Python 程序设计', capacity=2)
    c2 = Course('c002', '数据结构', capacity=3)

    # ---------- 4. 保存初始数据到数据库 ----------
    student_dao.save(s1)
    student_dao.save(s2)
    course_dao.save(c1)
    course_dao.save(c2)

    # ---------- 5. 执行选课操作 ----------
    print("=== 选课操作 ===")
    success = enroll_service.enroll(s1, c1)
    print(f"张三选 Python: {'成功' if success else '失败'}")   # 预期成功

    success = enroll_service.enroll(s1, c2)
    print(f"张三选数据结构: {'成功' if success else '失败'}")   # 预期成功

    success = enroll_service.enroll(s2, c1)
    print(f"李四选 Python: {'成功' if success else '失败'}")   # 预期成功（容量2，刚好满）



    
    
    # ---------- 6. 显示当前状态 ----------
    print("\n=== 当前状态 ===")
    print(s1)
    print(s2)
    print(c1)
    print(c2)

    # ---------- 7. 退课操作 ----------
    print("\n=== 退课操作 ===")
    success = enroll_service.drop(s1, c1)
    print(f"张三退选 Python: {'成功' if success else '失败'}")
    print(s1)
    print(c1)

    # ---------- 8. 重新加载验证持久化 ----------
    print("\n=== 从数据库重新加载 ===")
    s1_reload = student_dao.get_by_id('S001')
    c1_reload = course_dao.get_by_id('C001')
    print("重新加载的学生：", s1_reload)
    print("重新加载的课程：", c1_reload)

    # ---------- 9. 教师分配测试（扩展） ----------
    print("\n=== 教师分配（扩展） ===")
    t1 = Teacher('t001', '赵老师')
    t2 = Teacher('t005','小李')
    t3 = Teacher('t003','alice')
    t4 = Teacher('t004','小明')
    teacher_dao.save(t1)
    teacher_dao.save(t2)
    teacher_dao.save(t3)
    teacher_dao.save(t4)
    # 为赵老师分配 Python 课程
    teach_service.assign_teacher_to_course(t1, c1)
    # 再次查看课程信息，应包含教师
    c1_updated = course_dao.get_by_id('c001')
    print(c1_updated)
    t1_reload = teacher_dao.get_by_id('t001')
    print(t1_reload)

    # ---------- 10. 查询某课程的所有学生 ----------
    print("\n=== 查询课程《Python 程序设计》的学生列表 ===")
    students_in_c1 = enroll_service.list_students_in_course('c001')
    for stu in students_in_c1:
        print(stu)

    # 关闭数据库连接
    db.close()


if __name__ == '__main__':
    main()