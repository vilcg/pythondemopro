from flask import Flask, render_template, session, request, jsonify
from db import Database
from daos import TeacherDAO, StudentDAO, CourseDAO
from service import EnrollmentService,TeachingService
from auth import AuthManager, login_required, role_required

app = Flask(__name__)
app.secret_key = 'a-very-secret-key-for-session'

db = Database(host='localhost', user='root', password='c7386459', db='t2024')
student_dao = StudentDAO(db)
course_dao = CourseDAO(db)
teacher_dao = TeacherDAO(db)
enroll_service = EnrollmentService(db, student_dao, course_dao)
teach_service = TeachingService(db, teacher_dao, course_dao)
auth_manager = AuthManager(db)


# 把认证管理器存入应用配置，供装饰器使用
app.config['auth_manager'] = auth_manager


# 路由
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    #  简单校验：通过 query string 传递 token 或从 session 读取
    return render_template('dashboard.html')


# ==================== 认证 API ====================
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    token, user_info_or_msg = auth_manager.login(username, password)
    if token:
        return jsonify({'token': token, 'user': user_info_or_msg})
    return jsonify({'error': user_info_or_msg}), 401


@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    token = request.headers.get('Authorization')[7:]
    auth_manager.logout(token)
    return jsonify({'message': '已退出登录'})


# 此api没有应用上
@app.route('/api/register', methods=['POST'])
@login_required
@role_required('admin')
def api_register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    if not all([username, password, role]):
        return jsonify({'error': '参数不完整'}), 400
    if role not in ('admin', 'teacher', 'student'):
        return jsonify({'error': '无效的角色'}), 400
    try:
        auth_manager.register_user(username, password, role)
        return jsonify({'message': f'用户 {username} 创建成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 学生管理 API ====================
@app.route('/api/students', methods=['GET'])
@login_required
def api_get_students():
    students = student_dao.get_all()
    return jsonify([s.to_dict() for s in students])

@app.route('/api/students', methods=['POST'])
@login_required
@role_required('admin')
def api_create_student():
    data = request.get_json()
    sid = data.get('student_id')
    name = data.get('name')
    if not sid or not name:
        return jsonify({'error': '学号和姓名不能为空'}), 400
    student = models.Student(sid, name)  
    student_dao.save(student)
    return jsonify(student.to_dict()), 201


# ==================== 课程管理 API ====================
@app.route('/api/courses', methods=['GET'])
@login_required
def api_get_courses():
    courses = course_dao.get_all()
    return jsonify([c.to_dict() for c in courses])

@app.route('/api/courses', methods=['POST'])
@login_required
@role_required('admin')
def api_create_course():
    data = request.get_json()
    cid = data.get('course_id')
    name = data.get('course_name')
    capacity = data.get('capacity', 0)
    if not cid or not name or capacity <= 0:
        return jsonify({'error': '课程编号、名称和有效容量不能为空'}), 400
    course = models.Course(cid, name, capacity)
    course_dao.save(course)
    return jsonify(course.to_dict()), 201


# ==================== 选课/退课 API ====================
@app.route('/api/enroll', methods=['POST'])
@login_required
@role_required('student')
def api_enroll():
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    # 权限检查：学生只能操作自己的选课
    if request.current_user['username'] != student_id:  # 假设用户名即学号
        return jsonify({'error': '只能为自己选课'}), 403
    student = student_dao.get_by_id(student_id)
    course = course_dao.get_by_id(course_id)
    if not student or not course:
        return jsonify({'error': '学生或课程不存在'}), 404
    success, msg = enroll_service.enroll(student, course)
    if success:
        return jsonify({'message': msg})
    return jsonify({'error': msg}), 400

@app.route('/api/drop', methods=['POST'])
@login_required
@role_required('student')
def api_drop():
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    if request.current_user['username'] != student_id:
        return jsonify({'error': '只能自己退课'}), 403
    student = student_dao.get_by_id(student_id)
    course = course_dao.get_by_id(course_id)
    if not student or not course:
        return jsonify({'error': '学生或课程不存在'}), 404
    success, msg = enroll_service.drop(student, course)
    if success:
        return jsonify({'message': msg})
    return jsonify({'error': msg}), 400


# ==================== 教师分配 API ====================
@app.route('/api/assign-teacher', methods=['POST'])
@login_required
@role_required('admin')
def api_assign_teacher():
    data = request.get_json()
    teacher_id = data.get('teacher_id')
    course_id = data.get('course_id')
    teacher = teacher_dao.get_by_id(teacher_id)
    course = course_dao.get_by_id(course_id)
    if not teacher or not course:
        return jsonify({'error': '教师或课程不存在'}), 404
    success, msg = teach_service.assign_teacher_to_course(teacher, course)
    if success:
        return jsonify({'message': msg})
    return jsonify({'error': msg}), 400

@app.route('/api/teachers', methods=['GET'])
@login_required
def api_get_teachers():
    teachers = teacher_dao.get_all()
    return jsonify([t.to_dict() for t in teachers])


# 确保 models 被导入以创建实例
import models

if __name__ == '__main__':
    app.run(debug=True, port=5000)






