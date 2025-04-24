# tests/test_user_management.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from Ams_app.models import Shift

class UserManagerTests(TestCase):

    def setUp(self):
        # Create a sample shift to associate with users
        self.shift = Shift.objects.create(name="Morning", start_time="09:00", end_time="17:00")

    def test_create_user(self):
        """Test creating a user with email and password"""
        user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='testpassword123',
            shift=self.shift
        )
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertTrue(user.check_password('testpassword123'))
        self.assertEqual(user.shift, self.shift)
        self.assertEqual(user.role, 'Employee')  # Default role should be 'Employee'

    def test_create_superuser(self):
        """Test creating a superuser"""
        superuser = get_user_model().objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='adminpassword123',
            shift=self.shift
        )
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertEqual(superuser.name, 'Admin User')
        self.assertTrue(superuser.check_password('adminpassword123'))
        self.assertEqual(superuser.role, 'Admin')  # Role should be 'Admin'
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_user_without_email(self):
        """Test creating a user without an email raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                name='Test User',
                password='testpassword123'
            )

    def test_user_str_method(self):
        """Test the `__str__` method of the user"""
        user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='testpassword123',
            shift=self.shift
        )
        self.assertEqual(str(user), 'Test User')

    def test_user_default_role(self):
        """Test the default role is 'Employee'"""
        user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='testpassword123',
            shift=self.shift
        )
        self.assertEqual(user.role, 'Employee')

    def test_user_role_update(self):
        """Test the ability to update the user's role"""
        user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='testpassword123',
            shift=self.shift
        )
        user.role = 'Manager'
        user.save()
        self.assertEqual(user.role, 'Manager')
