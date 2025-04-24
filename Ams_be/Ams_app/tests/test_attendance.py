from rest_framework.test import APITestCase
from rest_framework import status
from django.utils.timezone import now
from datetime import date
from django.contrib.auth import get_user_model
from Ams_app.models import Attendance, Shift
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AttendanceTests(APITestCase):
    def setUp(self):
        # Create a Shift
        self.shift = Shift.objects.create(
            name="Morning",
            start_time="09:00:00",
            end_time="17:00:00"
        )

        # Create user and get token
        self.user = User.objects.create_user(
            email='employee@example.com',
            name='Employee One',
            password='strongpassword',
            role='Employee',
            shift=self.shift
        )
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_check_in_creates_attendance(self):
        response = self.client.post('/api/attendance/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Attendance.objects.filter(user=self.user, date=date.today()).exists())

    def test_check_out_updates_attendance(self):
        # First check-in
        self.client.post('/api/attendance/')
        # Then check-out
        response = self.client.post('/api/attendance/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        attendance = Attendance.objects.get(user=self.user, date=date.today())
        self.assertIsNotNone(attendance.check_out)

    def test_double_check_in_error(self):
        # First check-in
        self.client.post('/api/attendance/')
        # Attempting second check-in again on the same day
        response = self.client.post('/api/attendance/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Attempting third one should result in error
        response = self.client.post('/api/attendance/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_attendance_records(self):
        # Create attendance manually
        Attendance.objects.create(
            user=self.user,
            date=date.today(),
            check_in=now().time(),
            check_out=now().time(),
            status='Present'
        )
        response = self.client.get('/api/attendance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
