from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from Ams_app.models import User, LeaveRequest
from datetime import datetime

class LeaveRequestTests(APITestCase):
    
    def setUp(self):
        # Create test users (admin, HR, employee)
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com", name="Admin User", password="password123"
        )
        self.hr_user = User.objects.create_user(
            email="hr@test.com", name="HR User", role="Admin", password="password123"
        )
        self.employee_user = User.objects.create_user(
            email="employee@test.com", name="Employee User", password="password123"
        )

        # Create a LeaveRequest
        self.leave_request = LeaveRequest.objects.create(
            employee=self.employee_user,
            start_date=datetime.now().date(),
            end_date=datetime.now().date(),
            status="Pending",
        )

        # Create JWT tokens for authentication
        self.admin_token = RefreshToken.for_user(self.admin_user).access_token
        self.hr_token = RefreshToken.for_user(self.hr_user).access_token
        self.employee_token = RefreshToken.for_user(self.employee_user).access_token

    def test_hr_can_approve_leave_request(self):
        url = reverse('api:manage_leave_request', kwargs={'pk': self.leave_request.pk})
        response = self.client.put(
            url,
            {"status": "Approved"},
            HTTP_AUTHORIZATION=f"Bearer {self.hr_token}",
        )
        self.leave_request.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.leave_request.status, "Approved")
        self.assertEqual(self.leave_request.approved_by, self.hr_user)

    def test_employee_cannot_approve_leave_request(self):
        url = reverse('api:manage_leave_request', kwargs={'pk': self.leave_request.pk})
        response = self.client.put(
            url,
            {"status": "Approved"},
            HTTP_AUTHORIZATION=f"Bearer {self.employee_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_hr_cannot_approve_other_employee_leave_if_not_hr(self):
        url = reverse('api:manage_leave_request', kwargs={'pk': self.leave_request.pk})
        response = self.client.put(
            url,
            {"status": "Approved"},
            HTTP_AUTHORIZATION=f"Bearer {self.employee_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_can_create_leave_request(self):
        url = reverse('api:create_leave_request')
        data = {
            "start_date": datetime.now().date(),
            "end_date": datetime.now().date(),
            "status": "Pending"
        }
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=f"Bearer {self.employee_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_employee_cannot_create_leave_request_with_invalid_data(self):
        url = reverse('api:create_leave_request')
        data = {
            "start_date": "invalid_date",  # Invalid date
            "end_date": "invalid_date",    # Invalid date
            "status": "Pending"
        }
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=f"Bearer {self.employee_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_hr_can_approve_leave_request(self):
        url = reverse('api:manage_leave_request', kwargs={'pk': self.leave_request.pk})
        response = self.client.put(
            url,
            {"status": "Approved"},
            HTTP_AUTHORIZATION=f"Bearer {self.hr_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.leave_request.refresh_from_db()
        self.assertEqual(self.leave_request.status, "Approved")

    def test_employee_cannot_approve_leave_request(self):
        url = reverse('api:manage_leave_request', kwargs={'pk': self.leave_request.pk})
        response = self.client.put(
            url,
            {"status": "Approved"},
            HTTP_AUTHORIZATION=f"Bearer {self.employee_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
