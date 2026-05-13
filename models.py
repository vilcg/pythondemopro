# models.py
"""
实体类定义
- Person：基类，提供人员共有属性
- Student：学生类，包含选课/退课行为
- Course：课程类，包含添加/移除学生行为，容量控制
- Teacher：教师类，继承 Person，可分配课程
- 所有实体提供 to_dict() 方法用于 JSON 序列化
"""


class Person:
    """人员基类"""

    def __init__(self, person_id, name):
        self.person_id = person_id  # 编号（学号/工号）
        self.name = name            # 姓名

    def __str__(self):
        return f"ID: {self.person_id}, 姓名: {self.name}"


class Student:
    """学生实体"""

    def __init__(self, student_id, name, courses=None):
        self.student_id = student_id
        self.name = name
        # courses 列表可以存储课程ID（字符串）或 Course 对象
        self.courses = courses if courses is not None else []

    def enroll_in(self, course):
        """
        选课操作（学生侧）
        调用课程对象的 add_student，成功则记录课程
        返回 True（成功）或 False（失败，如容量满）
        """
        if course.add_student(self):
            self.courses.append(course)
            return True
        return False

    def drop_course(self, course):
        # 先从课程中移除学生
        if course.remove_student(self):
        # 兼容 courses 列表中既有对象又有字符串的情况
            target_cid = course.course_id if hasattr(course, 'course_id') else course
            for c in self.courses[:]:  # 用切片避免迭代时修改列表
                c_id = c.course_id if hasattr(c, 'course_id') else c
                if c_id == target_cid:
                    self.courses.remove(c)
                    return True
            return False
        return False
    # def drop_course(self, course):
    #     """
    #     退课操作（学生侧）
    #     调用课程对象的 remove_student，成功则移除本地记录
    #     """
    #     if course.remove_student(self):
    #         self.courses.remove(course)
    #         return True
    #     return False

    def to_dict(self):
        """
        序列化为字典，用于 JSON 存储
        courses 中统一输出为课程ID（字符串列表）
        """
        course_ids = []
        for c in self.courses:
            if isinstance(c, str):
                course_ids.append(c)
            else:
                course_ids.append(c.course_id)
        return {
            'student_id': self.student_id,
            'name': self.name,
            'courses': course_ids
        }

    def __str__(self):
        # 若 courses 中存的是 Course 对象，取出课程名；否则直接显示ID
        course_names = []
        for c in self.courses:
            if hasattr(c, 'course_name'):
                course_names.append(c.course_name)
            else:
                course_names.append(str(c))
        return f"学生ID: {self.student_id}, 姓名: {self.name}, 已选课程: {course_names}"


class Course:
    """课程实体"""

    def __init__(self, course_id, course_name, capacity, students=None, teacher_id=None):
        self.course_id = course_id
        self.course_name = course_name
        self._capacity = capacity          # 私有属性，通过 property 控制
        # students 列表可以存储学生ID（字符串）或 Student 对象
        self.students = students if students is not None else []
        self.teacher_id = teacher_id        # 可选扩展：授课教师ID

    @property
    def capacity(self):
        """课程容量（只允许通过 setter 修改，且受已选人数约束）"""
        return self._capacity

    @capacity.setter
    def capacity(self, value):
        """
        设置课程容量
        如果新容量小于当前已选学生数，则抛出异常，保证数据完整性
        """
        if value < len(self.students):
            raise ValueError("新容量不能小于当前已选课人数")
        self._capacity = value

    def add_student(self, student):
        """
        添加学生到课程（课程侧）
        成功条件：未满员
        返回 True 或 False
        """
        if len(self.students) < self._capacity:
            self.students.append(student)
            return True
        return False


    def remove_student(self, student):
        # student 可能是对象或 ID 字符串
        sid = student.student_id if hasattr(student, 'student_id') else student
        for s in self.students[:]:
            s_id = s.student_id if hasattr(s, 'student_id') else s
            if s_id == sid:
                self.students.remove(s)
                return True
        return False
    # def remove_student(self, student):
    #     """
    #     移除学生（课程侧）
    #     若 student 在列表中则移除，返回 True；否则 False
    #     """
    #     if student in self.students:
    #         self.students.remove(student)
    #         return True
    #     return False

    def to_dict(self):
        """
        序列化为字典
        students 中统一输出为学生ID（字符串列表）
        """
        student_ids = []
        for s in self.students:
            if isinstance(s, str):
                student_ids.append(s)
            else:
                student_ids.append(s.student_id)
        return {
            'course_id': self.course_id,
            'course_name': self.course_name,
            'capacity': self._capacity,
            'students': student_ids,
            'teacher_id': self.teacher_id
        }

    def __str__(self):
        student_names = []
        for s in self.students:
            if hasattr(s, 'name'):
                student_names.append(s.name)
            else:
                student_names.append(str(s))
        teacher_info = f", 授课教师: {self.teacher_id}" if self.teacher_id else ""
        return f"课程ID: {self.course_id}, 名称: {self.course_name}, 容量: {self._capacity}, 已选学生: {student_names}{teacher_info}"


class Teacher(Person):
    """教师实体，继承自 Person"""

    def __init__(self, teacher_id, name, courses_taught=None):
        super().__init__(teacher_id, name)      # person_id 即 teacher_id
        # courses_taught 列表可以存储课程ID（字符串）或 Course 对象
        self.courses_taught = courses_taught if courses_taught is not None else []

    def assign_to(self, course):
        """为教师分配授课课程（教师侧）"""
        if course not in self.courses_taught:
            self.courses_taught.append(course)

    def remove_course(self, course):
        """取消教师的授课课程"""
        if course in self.courses_taught:
            self.courses_taught.remove(course)

    def to_dict(self):
        """
        序列化为字典
        courses_taught 中统一输出为课程ID（字符串列表）
        """
        course_ids = []
        for c in self.courses_taught:
            if isinstance(c, str):
                course_ids.append(c)
            else:
                course_ids.append(c.course_id)
        return {
            'teacher_id': self.person_id,
            'name': self.name,
            'courses_taught': course_ids
        }

    def __str__(self):
        base = super().__str__()  # "ID: ..., 姓名: ..."
        course_names = []
        for c in self.courses_taught:
            if hasattr(c, 'course_name'):
                course_names.append(c.course_name)
            else:
                course_names.append(str(c))
        return f"{base}, 教授课程: {course_names}"