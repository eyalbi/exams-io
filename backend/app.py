import os

from flask import Flask, Response, request, render_template_string
from flask_mongoengine import MongoEngine
from flask_user import login_required, UserManager, UserMixin
from flask_user.forms import RegisterForm


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

    # Flask-User settings
    # Shown in and email templates and page footers
    USER_APP_NAME = "Flask-User MongoDB App"
    USER_ENABLE_EMAIL = False      # Disable email authentication
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form


app = Flask(__name__)
app.config.from_object(__name__+'.ConfigClass')

db = MongoEngine()
db.init_app(app)


class CustomRegisterForm(RegisterForm):
    role = StringField(_('Role'), validators=[DataRequired()])

# Define the User document.
# NB: Make sure to add flask_user UserMixin !!!


class User(db.Document, UserMixin):
    active = db.BooleanField(default=True)

    # User authentication information
    username = db.StringField(default='')
    password = db.StringField()

    # User information
    first_name = db.StringField(default='')
    last_name = db.StringField(default='')

    # Relationships
    roles = db.ListField(db.StringField(), default=[])


# Setup Flask-User and specify the User data-model
user_manager = UserManager(app, db, User)


# The Home page is accessible to anyone
@app.route('/')
def home_page():
    # String-based templates
    return render_template_string("""
        {% extends "flask_user_layout.html" %}
        {% block content %}
            <h2>Home page</h2>
            <p><a href={{ url_for('user.register') }}>Register</a></p>
            <p><a href={{ url_for('user.login') }}>Sign in</a></p>
            <p><a href={{ url_for('home_page') }}>Home page</a> (accessible to anyone)</p>
            <p><a href={{ url_for('member_page') }}>Member page</a> (login required)</p>
            <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
        {% endblock %}
        """)


# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/members')
@login_required    # User must be authenticated
def member_page():
    # String-based templates
    return render_template_string("""
        {% extends "flask_user_layout.html" %}
        {% block content %}
            <h2>Members page</h2>
            <p><a href={{ url_for('user.register') }}>Register</a></p>
            <p><a href={{ url_for('user.login') }}>Sign in</a></p>
            <p><a href={{ url_for('home_page') }}>Home page</a> (accessible to anyone)</p>
            <p><a href={{ url_for('member_page') }}>Member page</a> (login required)</p>
            <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
        {% endblock %}
        """)


if __name__ == '__main__':
    app.run()
