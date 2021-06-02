import unittest
from unittest.case import TestCase

from app import app
from models import User,Exams,Quiz_question,Quizz,StudentGrade

class TestRegister(unittest.TestCase):
    def setUp(self):
        TESTING = True
        WTF_CSRF_ENABLED = False
        app.testing = True
        app.config['WTF_CSRF_METHODS'] = []  # This is the magic
        self.app = app.test_client()
        User.objects(username='testuser').delete()

    def test_register(self):
        rv = self.app.post('/register',
                           data=dict(
                               username="testuser",
                                email="test@test.com",
                                password="1234", 
                                password2="1234", 
                                submit="Register",
                                first_name="test",
                                last_name="user",
                                role="Student",
                                avatar="https://robohash.org/3EC.png?set=set4"),
                           follow_redirects=True)
        self.assertIn(b'Congratulations, you are now a registered user!', rv.data)


class TestLogin(unittest.TestCase):
    def setUp(self):
        app.testing = True
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['WTF_CSRF_METHODS'] = []  # This is the magic
        self.app = app.test_client()

    def test_login(self):
        rv = self.app.post('/login',
        data=dict(username="testuser", password="1234", remember_me=False, submit="Sign In"),
        follow_redirects=True)
        self.assertIn(b'Hello', rv.data)


class TestUnauthenticated(unittest.TestCase):
    def setUp(self):
        app.testing = True
        app.config['WTF_CSRF_METHODS'] = []  # This is the magic
        self.app = app.test_client()

    def test_unauthenticated(self):
        rv = self.app.get('/index')
        self.assertNotEqual(rv.status, '200 OK')

class TestLecPersonalInfo(unittest.TestCase):
    def setUp(self):
        app.testing = True
        app.config['WTF_CSRF_METHODS'] = []  # This is the magic
        self.app = app.test_client()
        User.objects(username='testLec').delete()
        self.app.post('/register',
                        data=dict(
                            username="testLec",
                            email="test@test.com",
                            password="1234", 
                            password2="1234", 
                            submit="Register",
                            first_name="Lecturer",
                            last_name="Test",
                            role="Lecturer",
                            avatar="https://robohash.org/3EC.png?set=set4"),
                        follow_redirects=True)

    def test_lec_personal_info(self):
        with self.app:
            self.app.post('/login',
                            data=dict(username="testuser", password="1234", remember_me=False, submit="Sign In"),
                            follow_redirects=True)
            rv = self.app.get('/Lecturer/PersonalInfo', follow_redirects=True)
            print(rv.data)


if __name__ == '__main__':
    unittest.main()
