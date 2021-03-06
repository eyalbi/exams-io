from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FieldList, FormField

from wtforms.validators import DataRequired, Email, EqualTo
from models import ROLES, User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    role = SelectField('select role:', choices=[
                       ('Student', 'Student'), ('Lecturer', 'Lecturer'), ('Admin', 'Admin')])
    avatar = SelectField('select avatar:', choices=[('https://robohash.org/3EC.png?set=set4', 'cat1'), (
        'https://robohash.org/293.png?set=set4', 'cat2'), ('https://robohash.org/ZOB.png?set=set4', 'cat3')])
    submit = SubmitField('Register')


class AdminDeleteForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Delete')


class AdminBlockForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Block user')


class AdminUpdateForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    submit = SubmitField('update')


class AdminSendEmailForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')


class StudentMessage(FlaskForm):
    lecturer = StringField('lecturer', validators=[DataRequired()])
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')


class uploadExams(FlaskForm):
    Exam_name = StringField(default='')
    exam_pdf = FileField()
    exam_answer = FileField()
    submit = SubmitField('upload')


class QuestionCreateForm(FlaskForm):
    Question = StringField(default='')
    Answers = FieldList(StringField(default=''), min_entries=4)
    Correct_answer = StringField(default='')


class QuizzForm(FlaskForm):
    Quiz = FieldList(FormField(QuestionCreateForm), min_entries=3)
    Quizz_name = StringField('Quizz Name')
    submit = SubmitField('create Quiz')


class StudentSelectQuiz(FlaskForm):
    Lec_name = StringField(default='Enter Lecturer Username')
    submit = SubmitField('Find Quizes')


class StudentQuizForm(FlaskForm):
    def __init__(self, quiz):
        super().__init__()
        self.quizname = quiz
    quizname = StringField(default="")
    submit = SubmitField('Finish Quiz')


class LUpdateGrade(FlaskForm):
    StudentName = StringField(default="")
    quizname = StringField(default="")
    new_grade = StringField(default="")
    submit = SubmitField('Finish Quiz')


# class AdminUpdateForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     password2 = PasswordField(
#         'Repeat Password', validators=[DataRequired(), EqualTo('password')])
#     first_name = StringField('First Name', validators=[DataRequired()])
#     last_name = StringField('Last Name', validators=[DataRequired()])

    # def validate_username(self, username):
    #     user = User.query.filter_by(username=username.data).first()
    #     if user is not None:
    #         raise ValidationError('Please use a different username.')

    # def validate_email(self, email):
    #     user = User.query.filter_by(email=email.data).first()
    #     if user is not None:
    #         raise ValidationError('Please use a different email address.')
