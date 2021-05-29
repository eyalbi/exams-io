import unittest

from app import app

class TestRegister(unittest.TestCase):
    def setUp(self):
        TESTING = True
        WTF_CSRF_ENABLED = False
        app.testing = True
        app.config['WTF_CSRF_METHODS'] = []  # This is the magic
        self.app = app.test_client()

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
        data=dict(username="tar", password="1234", remember_me=False, submit="Sign In"),
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


if __name__ == '__main__':
    unittest.main()
