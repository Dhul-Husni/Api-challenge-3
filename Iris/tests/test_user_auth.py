import json
import datetime
from datetime import timedelta, datetime
import time

import jwt
from Iris.tests import base


class AuthTestCase(base.BaseApiTestCase):
    """Tests for the authentication blueprint"""

    def test_registration(self):
        """Tests if user registration works correctly"""
        res = self.client().post('/v2/auth/register', data=self.user_data)
        # get the results in json format
        result = json.loads(res.data.decode())
        self.assertEqual(result['Message'], 'You have successfully registered')
        self.assertEqual(res.status_code, 201)

    def test_registration_with_invalid_email(self):
        """Makes a post request to the api with invalid email and tests if user
        will be registered
        """
        res = self.client().post('/v2/auth/register', data={'First Name': 'Kali',
                                                            'Last Name': 'Siren',
                                                            'email': 'test@..com',
                                                            'password': 'Kali2018',
                                                            'Secret word': 'Kali2018'
                                                            })
        # get the result in json format
        result = json.loads(res.data.decode())
        self.assertEqual(result['message'], '400 Bad Request: Invalid Email Provided')

    def test_Registration_with_invalid_parameters(self):
        """Makes a post request to the api and not provide registration details """
        res = self.client().post('/v2/auth/register', data={'First INVALID KEY': 'Kali',
                                                            'Last INVALID KEY': 'Sir3n',
                                                            'email': 'test@gmail.com',
                                                            'password': 'Kali2018',
                                                            'Secret word': 'Kali2018'
                                                             })
        # get the result in json format
        result = json.loads(res.data.decode())
        self.assertIn("449 Retry With: Provide First Name, Last Name, email", result['message'])

    def test_registration_with_short_password_provided(self):
        """Makes a post request to the api with a password and tests if user
        will be registered"""
        res = self.client().post('/v2/auth/register', data={'First Name': 'Kali',
                                                            'Last Name': 'Sir3n',
                                                            'email': 'test@example.com',
                                                            'password': 'Kali2',
                                                            'Secret word': 'Kali2018'
                                                            })
        # get the result in json format
        result = json.loads(res.data.decode())
        self.assertEqual(result['message'], '411 Length Required: Password must be greater than 8')

    def test_login_password_mismatch(self):
        """Makes a post request to the api with wrong password and test login"""
        res = self.client().post('/v2/auth/register', data={'First Name': 'Kali',
                                                            'Last Name': 'Sir3n',
                                                            'email': 'test@example.com',
                                                            'password': 'Kali2018',
                                                            'Secret word': 'Kali2018'
                                                            })
        login_res = self.client().post('/v2/auth/login', data={
                                                                 'email': 'test@example.com',
                                                                 'password': 'INVALID PASSWORD'
                                                                 })
        res = json.loads(login_res.data.decode())
        self.assertEqual(res['Message'], 'Incorrect Email or Password')

    def test_user_login(self):
        """Test user login"""
        self.client().post('/v2/auth/register', data=self.user_data)
        login_res = self.client().post('/v2/auth/login', data=self.user_data)

        results = json.loads(login_res.data.decode())
        self.assertEqual(results['Message'], 'You have successfully logged in')

    def test_unregistered_user_login(self):
        none_exist = {
                      "email": "Kali@googligoo.com",
                      "password": "googligoo"
                     }
        login_res = self.client().post('/v2/auth/login', data=none_exist)
        result = json.loads(login_res.data.decode())
        self.assertEqual(result['Message'], 'Incorrect Email or Password')

    def test_already_registered(self):
        """Test register a user who is already registered"""
        self.client().post('/v2/auth/register', data=self.user_data)

        second_res = self.client().post('/v2/auth/register', data=self.user_data)
        result = json.loads(second_res.data.decode())
        self.assertEqual(result['Message'], 'User already exists. Please login')

    def test_user_logout(self):
        """Test user logout"""
        self.client().post('/v2/auth/register', data=self.user_data)
        login_res = self.client().post('/v2/auth/login', data=self.user_data)

        results = json.loads(login_res.data.decode())
        logout_res = self.client().post('/v2/auth/logout', headers=dict(Authorization=results['Access token']))
        results = json.loads(logout_res.data.decode())
        self.assertEqual(results['Message'], 'You have successfully logged out')

    def test_user_logout_with_no_token(self):
        """Test user logout with invalid token"""
        logout_res = self.client().post('/v2/auth/logout')
        results = json.loads(logout_res.data.decode())
        self.assertEqual(results['Message'], 'Please Provide an access token')

    def test_user_reset_password(self):
        """Test user reset password"""
        self.client().post('/v2/auth/register', data=self.user_data)

        reset_res = self.client().post('/v2/auth/reset-password', data={'password': 'NEW PASSWORD',
                                                                        'email': 'user1234@example.com',
                                                                        'Secret word': 'Kali2018'},
                                       )
        self.assertIn('Password updated successfully', str(reset_res.data))

    def test_user_reset_password_with_empty_strings(self):
        """Test user reset password with empty string"""
        self.client().post('/v2/auth/register', data=self.user_data)
        login_res = self.client().post('/v2/auth/login', data=self.user_data)

        results = json.loads(login_res.data.decode())
        self.assertTrue(results['Access token'])

        reset_res = self.client().post('/v2/auth/reset-password', data={'password': ''},
                                       headers=dict(Authorization=results['Access token']))
        self.assertIn('Please provide your email, Secret word and password', str(reset_res.data))

    def test_user_reset_password_with_invalid_secret_word(self):
        """Test user reset password with invalid secret word"""
        self.client().post('/v2/auth/register', data=self.user_data)
        reset_res = self.client().post('/v2/auth/reset-password', data={'password': 'NEW PASSWORD',
                                                                        'email': 'user1234@example.com',
                                                                        'Secret word': 'INVALID SECRET WORD'},
                                       headers=dict(Authorization='Invalid.token'))
        self.assertIn('401 unauthorized: invalid email or secret word', str(reset_res.data).lower())

    def test_user_reset_password_with_invalid_email(self):
        """Test user reset password with invalid email"""
        self.client().post('/v2/auth/register', data=self.user_data)
        reset_res = self.client().post('/v2/auth/reset-password', data={'password': 'NEW PASSWORD',
                                                                        'email': 'INVALID@TEST.COM',
                                                                        'Secret word': 'Kali2018'},
                                       headers=dict(Authorization='Invalid.token'))
        self.assertIn('401 unauthorized: invalid email or secret word', str(reset_res.data).lower())

    def test_user_login_with_expired_token(self):
        """
        Test user perform operations with invalid token
        :return: should not allow
        """
        payload = {
            'exp': datetime.utcnow() + timedelta(seconds=1),
            'iat': datetime.utcnow(),
            'sub': 1,
        }
        time.sleep(2)
        expired_token = jwt.encode(payload, 'sir3n.sn@gmail.com', algorithm='HS256')
        search_result = self.client().get('/v2/categories',
                                          headers=dict(Authorization=expired_token)
                                          )
        self.assertIn("Expired token. Please log in to get a new token", str(search_result.data))




