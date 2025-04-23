import pytest
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from Ams_app.models import Shift, Holiday
from django.contrib.auth import get_user_model

User = get_user_model()

class ShiftHolidayTests(APITestCase):

    def setUp(self):
        # Create superuser
        self.admin_user = User.objects.create_superuser(
            name='Raja',
            email='yallalarajareddy1@gmail.com',
            password='12345678'
        )

        # Create regular employee user
        self.employee_user = User.objects.create_user(
            name='Employee',
            email='employee@mail.com',
            password='employeepass'
        )

        # JWT token for admin
        login_url = reverse('token_obtain_pair')
        admin_response = self.client.post(login_url, {
            'email': 'yallalarajareddy1@gmail.com',
            'password': '12345678'
        }, format='json')
        self.admin_token = admin_response.data['access']

        # JWT token for employee
        employee_response = self.client.post(login_url, {
            'email': 'employee@mail.com',
            'password': 'employeepass'
        }, format='json')
        self.employee_token = employee_response.data['access']

        # URLs
        self.shift_url = reverse('api:shift_list_create')
        self.holiday_url = reverse('api:holiday_list_create')

    def test_admin_can_create_shift(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        shift_data = {
            'name': 'Day Shift',
            'start_time': '09:00:00',
            'end_time': '17:00:00',
        }
        response = self.client.post(self.shift_url, shift_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_employee_cannot_create_shift(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.employee_token)
        shift_data = {
            'start_time': '09:00:00',
            'end_time': '17:00:00',
            'shift_name': 'Day Shift'
        }
        response = self.client.post(self.shift_url, shift_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_holiday(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        holiday_data = {
            "name": "Holiday Name",
            "start_date": "2025-05-01",
            "end_date": "2025-05-05",
            "description": "Holiday description"
        }
        response = self.client.post(self.holiday_url, holiday_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_employee_cannot_create_holiday(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.employee_token)
        holiday_data = {
            'holiday_name': 'Christmas',
            'date': '2025-12-25'
        }
        response = self.client.post(self.holiday_url, holiday_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_all_shifts(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        Shift.objects.create(start_time="08:00:00", end_time="16:00:00", name="Morning Shift")
        response = self.client.get(self.shift_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_employee_cannot_view_all_shifts(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.employee_token)
        response = self.client.get(self.shift_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_all_holidays(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        Holiday.objects.create(name="New Year's Day", start_date="2025-01-01",end_date="2025-01-05")
        response = self.client.get(self.holiday_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_employee_cannot_view_all_holidays(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.employee_token)
        response = self.client.get(self.holiday_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
