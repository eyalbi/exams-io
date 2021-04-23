from models import User
import os
import smtplib
from email.message import EmailMessage

from flask import Flask, current_app, flash, Response, request, render_template_string, render_template, jsonify, redirect, url_for
from flask_mongoengine import MongoEngine
from bson.objectid import ObjectId
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_principal import Principal, Permission, RoleNeed, identity_changed, identity_loaded, Identity, AnonymousIdentity, UserNeed

from forms import LoginForm, RegistrationForm,AdminDeleteForm, AdminUpdateForm, AdminSendEmailForm,StudentMessage
from models import ROLES

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-MongoEngine settings
    MONGODB_SETTINGS = {
        'host': 'localhost:27017',
        'username': 'apiuser',
        'password': 'apipassword',
        'db': 'exams-io'
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
        if user.Blocked == 'true' or user.Blocked == 'True':
            flash('Your user is blocked adress Admin')
            return redirect(url_for('login'))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
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

def create_user(form):
    user = User(username=form.username.data, email=form.email.data)
    user.role = form.role.data
    user.first_name = form.first_name.data
    user.last_name = form.last_name.data
    user.set_password(form.password.data)
    user.avatar = form.avatar.data
    user.save()


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
    return render_template("exams.html", title='Exams Page')




@app.route('/Student/Messages', methods=['GET','POST'])
@login_required
def Student_messeges():
    u = User.objects(username=current_user.username).first()
    form = StudentMessage()
    if form.validate_on_submit():
        try:
            user = User.objects(username=form.lecturer.data,role = 'Lecturer').first()
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_password)
            msg = EmailMessage()
            msg.set_content(form.message.data)
            msg['Subject'] = 'A message from user {0} '.format(current_user.username)
            msg['From'] = gmail_user
            msg['To'] = user.email
            server.send_message(msg)
            server.quit()
        except:
            flash("no such Lecturer")
            return render_template("messages.html", title='Messages Page',user =u,form = StudentMessage())
    return render_template("messages.html", title='Messages Page',form = form,user = u)
       


@app.route('/Student/Grades')
@login_required
def Student_Grades():
    return render_template("Grades.html", title='Grades Page')


@app.route('/Student/PersonalInfo')
@login_required
def Student_personal_info():
    u = User.objects(username=current_user.username).first()
    return render_template("PersonalInfo.html", title='info Page', user=u)


@app.route('/Lecturer/Exams')
@login_required
def Lec_Exams():
    return render_template('UploadExams.html')


@app.route('/Lecturer/TechSupport', methods=['GET','POST'])
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
        msg['Subject'] = 'A message from user {0} '.format(current_user.username)
        msg['From'] = gmail_user
        msg['To'] = gmail_user
        server.send_message(msg)
        server.quit()
        return render_template("Lecturer.html", user=u)
    return render_template('AdminSendEmail.html', user=u,form=form)



@app.route('/Lecturer/Messages')
@login_required
def Lec_Messages():
    return render_template("messages.html", title='Messages Page')


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
            return render_template("Admin.html",user = u,message = "user Created Successfully") 
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
            return render_template("Admin.html",user =u ,message = "user Deleted Successfully")    
        return render_template("AdminDeleteUser.html",user=u,form=AdminDeleteForm())
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
                if user.role  == 'Admin':
                    flash("you cant Block Admin User !")
                    return render_template("Admin.html",user = u)
                User.objects(username=form.username.data).update(
                set__Blocked = "true"
            )
                return render_template("Admin.html",user = u,message = "user Blocked Successfully")    
        return render_template("AdminBlockUser.html",user=u,form=AdminBlockForm())
    except:
        flash('Error Blocking user')
        return redirect(url_for('admin_Block_user'))




@app.route('/admin/RegisterdUsers')
@login_required
@admin_permission.require(http_exception=403)
def admin_registerd_users():
    try:
        u = User.objects().limit(10)
        return render_template("AdminShowUsers.html",user = u) 
      
    except:
        flash('Error fetching users')
        return redirect(url_for('index'))

@app.route('/admin/BlockedUser')
@login_required
@admin_permission.require(http_exception=403)
def admin_Blocked_users():
    try:
        u = User.objects().limit(10)
        return render_template("BlockedUsers.html",user = u) 
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
            set__email = form.email.data,
            set__first_name= form.first_name.data,
            set__last_name =form.last_name.data
        )
        return render_template("Admin.html",user = u,message = "user updated Successfully") 
    return render_template("AdminUpdateInfo.html", user = u,form=AdminUpdateForm())
# except:
    #     flash('Error updating user')
    #     return redirect(url_for('admin_update_info'))


@app.route('/admin/sendEmail', methods=['GET','POST'])
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



