"""
TestCase for Model
"""
import unittest

from iris.models.user_model import User


class ApiTestModels(unittest.TestCase):
    """Tests the models for the database"""
    def test_password_does_not_have_read_or_write_permission(self):
        """Test for password does not have read or write permission"""
        person = User(email='sir3n.sn@gmail.com', password='Kali2018', first_name='person', last_name='grown_up')
        self.assertIn('Password is not a readable attribute', str(person.password))