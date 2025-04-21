
# 🕒 Attendance Management System – Backend

A robust backend system to manage employee attendance, leaves, shifts, and reporting, built using **Django** and **PostgreSQL** with secure **JWT Authentication**.

---

## 🚀 Features

- JWT-based login/register API
- Role-Based Access Control (Admin, Manager, Employee)
- Attendance tracking with validations
- Leave management system with approval flow
- Shift and Holiday management
- Filterable reports with pagination
- Standardized API responses
- Swagger API documentation
- End-to-end testing

---

## 🧱 Tech Stack

- **Framework**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (SimpleJWT)
- **Docs**: Swagger (drf-yasg)
- **Testing**: Django Test Framework
- **Others**: Git, Postman, Pre-commit Hooks

---

## 🛠️ Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yallalaraja/Attendance_Management_System-Team-Alpha-.git
cd Attendance_Management_System-Team-Alpha-
```

### 2. Setup Virtual Environment

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac:  source venv/bin/activate 
pip install -r requirements.txt
```

### 3. Configure PostgreSQL Database

Update `settings.py` with your PostgreSQL credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Ams_db',
        'USER': 'Ams_user',
        'PASSWORD': '12345678',
        'HOST': 'localhost',
        'PORT': 5432
    }
}
```

Then run:

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run the Server

```bash
python manage.py runserver
```

---

## 🔐 Authentication

- Uses **SimpleJWT** for token-based login
- Returns both access and refresh tokens
- Role-based permissions are enforced per endpoint

---

## 🌿 Branch Structure & Contributors

| Branch Name           | Description                         | Assigned To  |
|-----------------------|-------------------------------------|--------------|
| `dev-setup`           | Django project, DB setup            | Raja         |
| `dev-auth`            | Auth system, login/register, roles  | Kranthi      |
| `dev-attendance`      | Attendance APIs & logic             | Srikanth     |
| `dev-leave`           | Leave APIs, approval logic          | Vijitha      |
| `dev-shifts-holidays` | Shifts and Holiday models/APIs      | Ramu         |
| `dev-report-docs`     | Reports, Swagger, Postman, cleanup  | Harsha       |

✅ All features are merged into `main` after review & testing.

---

## 📄 API Documentation

Access Swagger docs at:

```
http://localhost:8000/swagger/
```

---

## 📬 Postman

Find the Postman collection at:

```
docs/postman_collection.json
```

---

## ✅ Final Checklist

- Run tests: `python manage.py test`
- Ensure clean code: pre-commit hooks
- All responses follow a standard API format

---

## 👨‍💻 Team Alpha

- **Raja** – Project setup, environment, docs
- **Kranthi** – Auth, login, roles
- **Srikanth** – Attendance management
- **Vijitha** – Leave workflows
- **Ramu** – Shifts & holidays
- **Harsha** – Reports, Swagger, testing

---

**Happy coding!** 🚀
```
