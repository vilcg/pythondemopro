# service.py（修改后的完整版本，替换原来的内容）
"""
服务层：协调 DAO 和实体，实现完整业务用例
所有方法返回 (success: bool, message: str)
"""


class EnrollmentService:
    """选课退课服务"""

    def __init__(self, db, student_dao, course_dao):
        self.db = db
        self.student_dao = student_dao
        self.course_dao = course_dao

    def _has_enrolled(self, student, course):
        """检查学生是否已选该课程"""
        # 存储的可能是对象或 ID，统一比较 course_id
        for c in student.courses:
            c_id = c.course_id if hasattr(c, 'course_id') else c
            if c_id == course.course_id:
                return True
        return False

    def enroll(self, student, course):
        """
        学生选课
        返回 (success, message)
        """
        with self.db.cursor():
            # 检查容量
            if len(course.students) >= course.capacity:
                return False, "课程容量已满"

            # 检查重复选课
            if self._has_enrolled(student, course):
                return False, "不能重复选课"

            # 执行选课
            if student.enroll_in(course):
                self.student_dao.save(student)
                self.course_dao.save(course)
                return True, "选课成功"
            return False, "选课失败"

    def drop(self, student, course):
        """
        学生退课
        返回 (success, message)
        """
        with self.db.cursor():
            if not self._has_enrolled(student, course):
                return False, "未选修该课程，无法退选"
            if student.drop_course(course):
                self.student_dao.save(student)
                self.course_dao.save(course)
                return True, "退课成功"
            return False, "退课失败"

    def list_students_in_course(self, course_id):
        """
        查询某门课程的所有学生（返回 Student 对象列表）
        """
        course = self.course_dao.get_by_id(course_id)
        if not course:
            return []
        students = []
        for sid in course.students:
            s = self.student_dao.get_by_id(sid)
            if s:
                students.append(s)
        return students


class TeachingService:
    """教师授课服务（扩展）"""

    def __init__(self, db, teacher_dao, course_dao):
        self.db = db
        self.teacher_dao = teacher_dao
        self.course_dao = course_dao

    def assign_teacher_to_course(self, teacher, course):
        """为教师分配课程"""
        with self.db.cursor():
            teacher.assign_to(course)
            course.teacher_id = teacher.person_id
            self.teacher_dao.save(teacher)
            self.course_dao.save(course)
            return True, "分配成功"

    def unassign_teacher_from_course(self, teacher, course):
        """取消教师与课程的关联"""
        with self.db.cursor():
            teacher.remove_course(course)
            if course.teacher_id == teacher.person_id:
                course.teacher_id = None
            self.teacher_dao.save(teacher)
            self.course_dao.save(course)
            return True, "取消分配成功"