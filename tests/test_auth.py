import unittest
import json

from app import create_app, db


class AuthTestCase(unittest.TestCase):
    """Tests for the authentication blueprint"""
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client
        self.user_data = {
            'First Name': 'Kali',
            'Last Name': 'Sir3n',
            'email': 'test@example.com',
            'password': 'test_password'
        }
        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_registration(self):
        """Tests if user registration works correctly"""
        res = self.client().post('/api-1.0/auth/register', data=self.user_data)
        # get the results in json format
        result = json.loads(res.data.decode())
        self.assertEqual(result['Message'], 'You have successfully registered')
        self.assertEqual(res.status_code, 201)

    def test_already_registered(self):
        """Test if user is already registerd"""
        res = self.client().post('/api-1.0/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)

        second_res = self.client().post('/api-1.0/auth/register', data=self.user_data)
        self.assertEqual(second_res.status_code, 202)
        result = json.loads(second_res.data.decode())
        self.assertEqual(result['Message'], 'User already exists. Please login')

    def test_user_login(self):
        """Test user login"""
        res = self.client().post('/api-1.0/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api-1.0/auth/login', data=self.user_data)

        results = json.loads(login_res.data.decode())
        self.assertEqual(results['Message'], 'You have successfully logged in')
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(results['Access token'])

    def test_unregistered_user_login(self):
        None_exist = {
            "email": "Kali@googligoo.com",
            "password": "googligoo"
        }
        login_res = self.client().post('/api-1.0/auth/login', data=None_exist)
        result = json.loads(login_res.data.decode())
        self.assertEqual(login_res.status_code, 401)
        self.assertEqual(result['Message'], 'Email address does not match any. Please try again')

