from rest_framework.test import APITestCase
from django.urls import reverse
from .models import User, Shift, Attendance, LeaveRequest, Holiday, UserShiftAssignment
from django.utils import timezone
from datetime import timedelta


# BaseTestCase with common setup
class BaseTestCase(APITestCase):
    def setUp(self):
        # Create admin and employee users
        self.admin = User.objects.create_user(email="admin@test.com", password="admin123", role="Admin")
        self.employee = User.objects.create_user(email="emp@test.com", password="emp123", role="Employee")
        
        # Create a shift
        self.shift = Shift.objects.create(name="Morning", start_time="09:00", end_time="17:00")
        self.employee.shift = self.shift
        self.employee.save()
        
        # URL names
        self.login_url = reverse("token_obtain_pair")
        self.shift_url = reverse("shift-list")
        self.assignment_url = reverse("usershiftassignment-list")
        self.attendance_url = reverse("attendance-list")
        self.leave_url = reverse("leaverequest-list")
        self.holiday_url = reverse("holiday-list")


# Test User Login
class UserLoginTests(BaseTestCase):
    def test_employee_login(self):
        response = self.client.post(self.login_url, {
            "email": "emp@test.com",
            "password": "emp123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)


# Test Shift Creation
class ShiftTests(BaseTestCase):
    def test_create_shift(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.shift_url, {
            "name": "Night",
            "start_time": "22:00",
            "end_time": "06:00",
            "is_active": True
        })
        self.assertEqual(response.status_code, 201)


# Test Assign User to Shift
class UserShiftAssignmentTests(BaseTestCase):
    def test_assign_user_to_shift(self):
        self.client.force_authenticate(user=self.admin)
        today = timezone.now().date()
        response = self.client.post(self.assignment_url, {
            "user": self.employee.id,
            "shift": self.shift.id,
            "date": today
        })
        self.assertEqual(response.status_code, 201)


# Test Attendance Check-In
class AttendanceTests(BaseTestCase):
    def test_attendance_check_in(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.post(self.attendance_url, {
            "check_in": timezone.now()
        })
        self.assertEqual(response.status_code, 201)


# Test Attendance Check-Out
class AttendanceCheckoutTests(BaseTestCase):
    def test_attendance_check_out(self):
        self.client.force_authenticate(user=self.employee)
        checkin = Attendance.objects.create(user=self.employee, check_in=timezone.now())
        response = self.client.post(self.attendance_url, {
            "check_out": timezone.now() + timedelta(hours=6)
        })
        self.assertEqual(response.status_code, 201)


# Test Apply Leave Request
class LeaveRequestTests(BaseTestCase):
    def test_apply_leave(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.post(self.leave_url, {
            "leave_type": "Sick",
            "start_date": timezone.now().date(),
            "end_date": timezone.now().date(),
            "reason": "Not well"
        })
        self.assertEqual(response.status_code, 201)


# Test Admin Approves Leave Request
class AdminLeaveApprovalTests(BaseTestCase):
    def test_admin_approves_leave(self):
        self.client.force_authenticate(user=self.admin)
        leave = LeaveRequest.objects.create(employee=self.employee, leave_type="Sick", reason="Test")
        response = self.client.patch(reverse("leaverequest-admin-detail", args=[leave.id]), {
            "status": "Approved"
        })
        self.assertEqual(response.status_code, 200)


# Test Create Holiday
class HolidayTests(BaseTestCase):
    def test_create_holiday(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.holiday_url, {
            "name": "Independence Day",
            "start_date": "2025-08-15",
            "end_date": "2025-08-15"
        })
        self.assertEqual(response.status_code, 201)


# Test Shift Access Logic
class ShiftAccessTests(BaseTestCase):
    def test_check_shift_time_access(self):
        self.client.force_authenticate(user=self.employee)
        UserShiftAssignment.objects.create(user=self.employee, shift=self.shift, date=timezone.now().date())
        response = self.client.get(reverse("shift-assignment-check"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("within_shift", response.data)


# Test: User Registration (for completeness)
class UserRegistrationTests(BaseTestCase):
    def test_user_registration(self):
        response = self.client.post(reverse('user-list'), {
            "email": "newuser@test.com",
            "password": "password123",
            "role": "Employee"
        })
        self.assertEqual(response.status_code, 201)
