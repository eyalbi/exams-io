from models import User, Exams, Quiz_question, Quizz, StudentGrade
import os
import smtplib
from email.message import EmailMessage


from flask import Flask, current_app, flash, Response, request, render_template_string, render_template, jsonify, redirect, url_for, session, send_file

from flask_mongoengine import MongoEngine
from bson.objectid import ObjectId
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_principal import Principal, Permission, RoleNeed, identity_changed, identity_loaded, Identity, AnonymousIdentity, UserNeed
from werkzeug.utils import secure_filename

from forms import LoginForm, RegistrationForm, AdminDeleteForm, LUpdateGrade, AdminUpdateForm, AdminSendEmailForm, StudentMessage, uploadExams, QuestionCreateForm, QuizzForm, StudentSelectQuiz, StudentQuizForm,AdminBlockForm
from models import ROLES

# Class-based application configuration
PATH = './uploads/'

class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-MongoEngine settings
    MONGODB_SETTINGS = {
        # 'host': 'mongodb://bendbil.byfy8.mongodb.net/exams-io?retryWrites=true&w=majority',
        'username': 'apiuser',
        'password': '1234abcd',
        'db': 'exams-io',
        'host': 'mongodb+srv://apiuser:1234abcd@bendbil.byfy8.mongodb.net/exams-io?retryWrites=true&w=majority'
    }


app = Flask(__name__)
app.config.from_object(__name__+'.ConfigClass')

db = MongoEngine()
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# create role based auth
principals = Principal(app)
admin_permission = Permission(RoleNeed('Admin'))
student_permission = Permission(RoleNeed('Student'))
lecturer_permission = Permission(RoleNeed('Lecturer'))

gmail_user = 'examsiomail@gmail.com'
gmail_password = '1q2w#E$R'


@login_manager.user_loader
def load_user(user_id):
    return User.objects.get(id=user_id)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'role'):
        identity.provides.add(RoleNeed(current_user.role))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        if user.Blocked == 'true' or user.Blocked == 'True':
            flash('Your user is blocked adress Admin')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        identity_changed.send(current_app._get_current_object(),
                              identity=Identity(user.username))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    try:
        form = RegistrationForm()
        if form.validate_on_submit():

            create_user(form)
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)
    except:
        flash('username Already exists')
        return redirect('/register')


def create_exam(form):
    exam_pdf = form.exam_pdf.data
    exam_answer = form.exam_answer.data
    exam_pdf_filename = secure_filename(exam_pdf.filename)
    exam_answer_filename = secure_filename(exam_answer.filename)

    exam_pdf.save(os.path.join(PATH, exam_pdf_filename))
    exam_answer.save(os.path.join(PATH, exam_answer_filename))

    exam = Exams(Exam_name=form.Exam_name.data,
                 exam_pdf=exam_pdf_filename, exam_answer=exam_answer_filename)
    exam.save()


def create_user(form):
    user = User(username=form.username.data, email=form.email.data)
    user.role = form.role.data
    user.first_name = form.first_name.data
    user.last_name = form.last_name.data
    user.set_password(form.password.data)
    user.avatar = form.avatar.data
    user.save()


@app.route('/download')
def downloadFile ():
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = os.path.join(PATH, request.args['path'])
    return send_file(path, as_attachment=True)

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = User.objects(username=current_user.username).first()
    if user.role == 'Student':
        return render_template('Student.html', user=user)
    elif user.role == 'Lecturer':
        return render_template('Lecturer.html', user=user)
    elif user.role == 'Admin':
        return render_template("Admin.html", user=user)
    else:
        return redirect(url_for('index'))


@app.route('/Student/Exams')
@login_required
def Student_exams():
    exams = Exams.objects()
    u = User.objects(username=current_user.username).first()
    return render_template("exams.html", title='Exams Page', exams=exams, user=u)


@app.route('/Student/Messages', methods=['GET', 'POST'])
@login_required
def Student_messeges():
    u = User.objects(username=current_user.username).first()
    form = StudentMessage()
    if form.validate_on_submit():
        try:
            user = User.objects(username=form.lecturer.data,
                                role='Lecturer').first()
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_password)
            msg = EmailMessage()
            msg.set_content(form.message.data)
            msg['Subject'] = 'A message from user {0} '.format(
                current_user.username)
            msg['From'] = gmail_user
            msg['To'] = user.email
            server.send_message(msg)
            server.quit()
        except:
            flash("no such Lecturer")
            return render_template("messages.html", title='Messages Page', user=u, form=StudentMessage())
    return render_template("messages.html", title='Messages Page', form=form, user=u)


@app.route('/Student/Quizes', methods=['GET', 'POST'])
@login_required
def Student_Quizes():
    u = User.objects(username=current_user.username).first()
    form = StudentSelectQuiz()
    if form.validate_on_submit():
        Quizes = Quizz.objects(Lec_name=form.Lec_name.data)
        return render_template("SQuizes.html", title='Quizes Page', Quizes=Quizes, user=u)
    return render_template("Search_quiz.html", title='Quizes Page', user=u, form=form)


@app.route('/Student/takeQuiz', methods=['GET', 'POST'])
@login_required
def Studnet_quiz_try():
    u = User.objects(username=current_user.username).first()
    form = StudentQuizForm(request.form['quiz'])
    Quiz = Quizz.objects(quizname=request.form['quiz']).first()
    if form.validate_on_submit():
        print(request.form['1'])
        SGrade = StudentGrade(
            StudentName=current_user.username, quizname=form.quizname)
        grade = 0
        i = 0
        for q in Quiz.questions:
            if q.Correct_answer == request.form[i]:
                grade += 1
            i += 1
        SGrade.Grade = (grade / len(Quiz.questions)) * 100
        lec = User.objects(username=Quiz.Lec_name).first()
        print(lec.username)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        msg = EmailMessage()
        msg.set_content("empty")
        msg['Subject'] = 'Student {0} did your test and got {1}'.format(
            current_user.username, SGrade.Grade)
        msg['From'] = gmail_user
        msg['To'] = lec.email
        server.send_message(msg)
        server.quit()
        return redirect('/')
    return render_template("AnswerQuiz.html", title='Quizes Page', user=u, form=form, Quiz=Quiz)


@app.route('/Student/Quizgrade', methods=['GET', 'POST'])
@login_required
def get_grade():
    Quiz = Quizz.objects(quizname=request.form['quiz']).first()
    SGrade = StudentGrade(StudentName=current_user.username,
                          quizname=request.form['quiz'])
    grade = 0
    i = 0
    for q in Quiz.questions:
        if q.Correct_answer == request.form.getlist('checked')[i]:
            grade += 1
        i += 1
    SGrade.Grade = str((grade / len(Quiz.questions)) * 100)
    SGrade.save()
    return redirect('/')


@app.route('/Student/GradesAverage')
@login_required
def Student_Grades_average():
    grades = StudentGrade.objects(StudentName = current_user.username)
    counter = 0 
    avg = 0
    avgDic = {}
    for Q in grades:
        Qgrades = StudentGrade.objects(quizname = Q.quizname)
        for q in Qgrades:
            avg += float(q.Grade)
            counter += 1
        avgDic[Q.quizname] = avg / counter
    return render_template("GradesAverage.html", title='Grades Page',avgDic = avgDic)

@app.route('/Student/Grades')
@login_required
def Student_Grades():
    grades = StudentGrade.objects(StudentName = current_user.username)
    GDic = dict((q.quizname,q.Grade) for q in grades)
    return render_template("Grades.html", title='Grades Page',GDic = GDic)

@app.route('/Student/emailGrades')
@login_required
def Student_Grades_email():
    grades = StudentGrade.objects(StudentName = current_user.username)
    GDic = dict((q.quizname,q.Grade) for q in grades)
    gradeMessage = ""
    for x in GDic:
        gradeMessage += "{0} : {1}\n".format(x,GDic[x])
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(gmail_user, gmail_password)
    msg = EmailMessage()
    msg.set_content(gradeMessage)
    msg['Subject'] = 'your Grades'
    msg['From'] = gmail_user
    msg['To'] = current_user.email
    server.send_message(msg)
    server.quit()
    return render_template("Grades.html", title='Grades Page',GDic = GDic)

@app.route('/Student/PersonalInfo')
@login_required
def Student_personal_info():
    u = User.objects(username=current_user.username).first()
    return render_template("PersonalInfo.html", title='info Page', user=u)


@app.route('/Lecturer/Exams', methods=['GET', 'POST'])
@login_required
def Lec_Exams():
    u = User.objects(username=current_user.username).first()
    form = uploadExams()
    try:
        if form.validate_on_submit():
            create_exam(form)
            flash('Upload succesufll!')
            return redirect(url_for('index'))
        return render_template('UploadExams.html', title='UploadExams', form=form, user=u)
    except Exception as ex:
        print(ex)
        flash('cant upload document')
        return redirect('index')


@app.route('/Lecturer/TechSupport', methods=['GET', 'POST'])
@login_required
def Lec_supprot():
    u = User.objects(username=current_user.username).first()
    form = AdminSendEmailForm()
    if form.validate_on_submit():
        users = User.objects()
        # emails = [user.email for user in users]

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        msg = EmailMessage()
        msg.set_content(form.message.data)
        msg['Subject'] = 'A message from user {0} '.format(
            current_user.username)
        msg['From'] = gmail_user
        msg['To'] = gmail_user
        server.send_message(msg)
        server.quit()
        return render_template("Lecturer.html", user=u)
    return render_template('AdminSendEmail.html', user=u, form=form)


@app.route('/Lecturer/Messages')
@login_required
def Lec_Messages():
    u = User.objects(username=current_user.username).first()
    mail = u.email
    domain = "https://" + mail.split("@")[-1]
    return render_template("LeC_messages.html", title='Messages Page', user=u, domain=domain)


@app.route('/Lecturer/Quizzes', methods=['GET'])
@login_required
def Lec_Quizzes():
    u = User.objects(username=current_user.username).first()
    quizzes = Quizz.objects(Lec_name=u.username)
    return render_template("Quizzes.html", user=u, quizzes=quizzes)


@app.route('/Lecturer/CreateQuiz', methods=['GET', 'POST'])
@login_required
def Lec_CreateQuiz():
    u = User.objects(username=current_user.username).first()
    form = QuizzForm()
    # try:
    if form.validate_on_submit():
        quiz = Quizz(Lec_name=current_user.username,
                     quizname=form.Quizz_name.data)
        for q in form.Quiz:
            answers = list(map(lambda a: a.data, q.Answers))
            ques = Quiz_question(
                Question=q.Question.data, Correct_answer=q.Correct_answer.data, Answers=answers)
            quiz.questions.append(ques)
        quiz.save()

        return redirect('/index')
    return render_template('createquiz.html', title='createquiz', form=form, user=u)
    # except:
    #     flash('cant upload document')
    #     return redirect('/index')


@app.route('/Lecturer/EditGrade', methods=['GET', 'POST'])
@login_required
def Lec_edit_grade():
    u = User.objects(username=current_user.username).first()
    form = LUpdateGrade()
    if form.validate_on_submit():
        if Quizz.objects(Lec_name=current_user.username, quizname=form.quizname.data).first():
            StudentGrade.objects(StudentName=form.StudentName.data, quizname=form.quizname.data).update(
                set__Grade=form.new_grade.data
            )
        flash("Grade was edited seccesfuly")
        return redirect('/')
    return render_template("EditGrades.html", title='info Page', user=u, form=form)


@app.route('/Lecturer/PersonalInfo')
@login_required
def Lec_personal_info():
    u = User.objects(username=current_user.username).first()
    return render_template("PersonalInfo.html", title='info Page', user=u)


@app.route('/admin/createUser', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def admin_create_user():
    u = User.objects(username=current_user.username).first()

    try:
        form = RegistrationForm()
        if form.validate_on_submit():
            create_user(form)
            return render_template("Admin.html", user=u, message="user Created Successfully")
        return render_template("AdminCreateUser.html", user=u, form=RegistrationForm())
    except:
        flash('Error creating user')
        return redirect(url_for('admin_create_user'))


@app.route('/admin/DeleteUser', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def admin_Delete_user():
    try:
        u = User.objects(username=current_user.username).first()
        form = AdminDeleteForm()
        if form.validate_on_submit():
            u = User.objects(username=form.username.data).first()
            u.delete()
            return render_template("Admin.html", user=u, message="user Deleted Successfully")
        return render_template("AdminDeleteUser.html", user=u, form=AdminDeleteForm())
    except:
        flash('Error Deleting user')
        return redirect(url_for('admin_Delete_user'))


@app.route('/admin/BlockUser', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def admin_Block_user():
    try:
        u = User.objects(username=current_user.username).first()
        form = AdminBlockForm()
        if form.validate_on_submit():
            user = User.objects(username=form.username.data).first()
            if user:
                if user.role == 'Admin':
                    flash("you cant Block Admin User !")
                    return render_template("Admin.html", user=u)
                User.objects(username=form.username.data).update(
                    set__Blocked="true"
                )
                return render_template("Admin.html", user=u, message="user Blocked Successfully")
        return render_template("AdminBlockUser.html", user=u, form=AdminBlockForm())
    except:
        flash('Error Blocking user')
        return redirect(url_for('admin_Block_user'))


@app.route('/admin/RegisterdUsers')
@login_required
@admin_permission.require(http_exception=403)
def admin_registerd_users():
    try:
        u = User.objects().limit(10)
        return render_template("AdminShowUsers.html", user=u)

    except:
        flash('Error fetching users')
        return redirect(url_for('index'))


@app.route('/admin/BlockedUser')
@login_required
@admin_permission.require(http_exception=403)
def admin_Blocked_users():
    try:
        u = User.objects().limit(10)
        return render_template("BlockedUsers.html", user=u)
    except:
        flash('Error fetching users')
        return redirect(url_for('index'))


@app.route('/admin/updateInfo', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def admin_update_info():
    u = User.objects(username=current_user.username).first()
    form = AdminUpdateForm()
    if form.validate_on_submit():
        User.objects(username=current_user.username).update(
            set__email=form.email.data,
            set__first_name=form.first_name.data,
            set__last_name=form.last_name.data
        )
        return render_template("Admin.html", user=u, message="user updated Successfully")
    return render_template("AdminUpdateInfo.html", user=u, form=AdminUpdateForm())
# except:
    #     flash('Error updating user')
    #     return redirect(url_for('admin_update_info'))


@app.route('/admin/sendEmail', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def admin_send_email():
    u = User.objects(username=current_user.username).first()
    form = AdminSendEmailForm()
    if form.validate_on_submit():
        users = User.objects()
        emails = [user.email for user in users]
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        msg = EmailMessage()
        msg.set_content(form.message.data)
        msg['Subject'] = 'A message from exams-io admin'
        msg['From'] = gmail_user
        msg['To'] = emails
        server.send_message(msg)
        server.quit()
        return render_template("AdminSendEmail.html", user=u, form=form)
    return render_template("AdminSendEmail.html", user=u, form=form)


if __name__ == '__main__':
    app.run()
