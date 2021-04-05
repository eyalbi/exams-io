from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_mongoengine import MongoEngine

ROLES = ('Student', 'Lecturer', 'Admin')

db = MongoEngine()
class User(UserMixin, db.Document):
    # User authentication information
    username = db.StringField(default='')
    password_hash = db.StringField()
    email = db.EmailField()
    # User information
    first_name = db.StringField(default='')
    last_name = db.StringField(default='')

    # Relationships
    role = db.StringField(default='', choices = ROLES)

    def get_role (self):
        return self.role
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
