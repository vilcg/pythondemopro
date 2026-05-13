from flask import Flask, render_template,request, redirect, url_for
from db import Database
from daos import StudentDAO, CourseDAO, TeacherDAO
from service import EnrollmentService
from models import Student, Course, Teacher


app = Flask(__name__)

# 初始化数据库连接
db = Database(host='localhost',user='root',password='c7386459',db='t2024')

# 初始化DAO和服务
student_dao = StudentDAO(db)
course_dao = CourseDAO(db)
teacher_dao = TeacherDAO(db)
service = EnrollmentService(db, student_dao, course_dao, teacher_dao)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enroll',methods=['GET','POST'])
def enroll():
    if request.method == 'GET':
         # GET请求：显示选课页面，让用户输入学号和课程号
        return render_template('enroll.html')
    else:
         # POST请求：提供输入
        student_id =  request.form.get('student_id')
        course_id = request.form.get('course_id')
        student = student_dao.get_by_id(student_id)
        course = course_dao.get_by_id(course_id)
        if student and course:
            success,msg = service.enroll(student,course)
        else:
            success,msg = False,"学生或课程不存在"
        return render_template('result.html',success=success,msg=msg)

@app.route('/drop',methods=['GET','POST'])
def drop():
    if request.method == 'GET':
        return render_template('drop.html',type='drop')
    else:
        student_id =  request.form.get('student_id')
        course_id = request.form.get('course_id')
        student = student_dao.get_by_id(student_id)
        course = course_dao.get_by_id(course_id)
        if student and course:
            success,msg = service.drop(student,course)
        else:
            success,msg = False,"学生或课程不存在"
        return render_template('result.html',success=success,msg=msg)


@app.route('/query',methods=['GET','POST'])
def query():
    if request.method == 'GET':
        return render_template('query.html')
    else:
        course_id = request.form.get("course_id")
        course = course_dao.get_by_id(course_id)
        
        if not course:
            return render_template('result.html',success=False,msg="课程不存在")
        
        students = []
        for s in course.students:
            stu = student_dao.get_by_id(s)
            if stu:
                students.append(stu)
        return render_template('query.html', students=students, course_name=course.course_name)

@app.route('/result')
def result():
    return render_template('result.html')



if __name__ == '__main__':
    app.run(debug=True)
