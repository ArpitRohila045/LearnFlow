"Learn Flow" 

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐
│   Frontend      │
│  (React/Vue)    │
└────────┬────────┘
         │ REST API
         │
┌────────▼────────┐
│  Django REST    │
│   Framework     │
├─────────────────┤
│  Authentication │
│   (JWT Tokens)  │
├─────────────────┤
│   Permissions   │
│   & Authorization│
├─────────────────┤
│  Business Logic │
│    (Views)      │
├─────────────────┤
│  ORM Models     │
└────────┬────────┘
         │
┌────────▼────────┐
│   PostgreSQL    │
│    Database     │
└─────────────────┘
```

### Component Breakdown

**1. User Management Layer**
- Custom User model with role-based access (Student, Teacher, Admin)
- Extended profiles for Students and Teachers
- Email-based authentication

**2. Academic Structure Layer**
- Course → Section → Subject hierarchy
- Many-to-many relationship between Teachers and Sections
- SectionSubject as the central junction table

**3. Content Management Layer**
- Announcements (Global & Section-specific)
- Syllabus uploads
- Assignments with submissions
- Quizzes with questions and attempts

**4. Performance Tracking Layer**
- Marks with categories (Mid-term, Final, etc.)
- Attendance tracking
- Discussion forums

---

## 🗄️ Database Schema Overview

### Core Entities Relationship

```
User (Custom)
├── role: STUDENT | TEACHER | ADMIN
├──┬─► StudentProfile
│  └─► Section ──► Course
└──┬─► TeacherProfile
   └─► SectionSubject (M2M)

Section
├─► Course
└─► SectionSubject ◄─► Subject
    └─► Teachers (M2M)

SectionSubject (Junction Table)
├─► Announcements
├─► Syllabus
├─► Assignments ──► AssignmentSubmissions
├─► Quizzes ──► QuizAttempts
├─► DiscussionThreads ──► Replies
├─► StudentMarks
└─► Attendance
```

### Key Database Design Decisions

**1. SectionSubject as Central Entity**
- Acts as the junction between Section and Subject
- Stores many-to-many relationship with Teachers
- All course materials link to SectionSubject (not just Section or Subject)
- Allows same subject to be taught differently in different sections

**2. Normalized Structure**
- Prevents data redundancy
- Ensures data integrity
- Allows flexible teacher assignments

**3. Soft Deletes**
- `is_active` flags instead of hard deletes
- Maintains historical data
- Allows data recovery

---

## 🔐 Authentication & Authorization

### User Roles & Permissions

| Role | Access Level |
|------|-------------|
| **Student** | - View enrolled subjects<br>- Submit assignments<br>- Attempt quizzes<br>- View own marks<br>- Participate in discussions |
| **Teacher** | - View assigned sections<br>- Create/grade assignments<br>- Create quizzes<br>- Post announcements<br>- Mark attendance<br>- View all student stats |
| **Admin** | - Full system access<br>- Manage users<br>- Create courses/sections<br>- Assign teachers |

### Permission Classes

**Custom Permissions Implemented:**

```python
IsStudent - Checks user.role == 'STUDENT'
IsTeacher - Checks user.role == 'TEACHER'
IsAdmin - Checks user.role == 'ADMIN'
IsTeacherOfSection - Verifies teacher teaches the section
IsStudentOfSection - Verifies student belongs to the section
```

### Authentication Flow

```
1. User Login → Email & Password
2. Django validates credentials
3. JWT Token generated (Access + Refresh)
4. Frontend stores token
5. All API calls include Bearer token
6. Backend validates token + permissions
7. Response sent if authorized
```

---

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
pip install django djangorestframework
pip install djangorestframework-simplejwt
pip install pillow  # For image uploads
pip install psycopg2-binary  # For PostgreSQL
```

### 2. Configure Django Settings

```python
# settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'your_app_name',
]

AUTH_USER_MODEL = 'your_app_name.User'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'course_management_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser

---

## 🎯 Key Features Implementation

### 1. Student Dashboard

**What Students See:**
- All enrolled subjects with teacher names
- Upcoming assignment deadlines
- Recent announcements (global + subject-specific)
- Current average marks per subject
- Unread discussion count

**Implementation:**
```python
# Fetch student's section → Get all section_subjects → 
# Aggregate data from announcements, assignments, marks
```

### 2. Teacher Dashboard

**What Teachers See:**
- All sections they teach
- Student count per section
- Pending submissions to grade
- Recent discussion activity

**Implementation:**
```python
# Query SectionSubject.objects.filter(teachers=current_teacher)
# For each section → Calculate stats
```

### 3. Marks & Performance Tracking

**Features:**
- Category-wise marks (Mid-term, Final, etc.)
- Automatic percentage calculation
- Historical tracking
- Average calculation across subjects

**Implementation:**
```python
# StudentMarks model with MarksCategory
# Use Django aggregation: Avg(), Sum()
# Calculate weighted average based on category weightage
```

### 4. Discussion Channel

**Features:**
- Subject-specific discussions
- Threaded replies (nested comments)
- Pin important threads
- Lock threads to prevent new replies

**Implementation:**
```python
# DiscussionThread → DiscussionReply (self-referential FK)
# parent_reply field allows nested structure
```

### 5. Assignment Submission & Grading

**Workflow:**
1. Teacher creates assignment with due date
2. Students submit files before deadline
3. Late submissions marked automatically
4. Teacher grades and provides feedback
5. Students view grades and feedback

**Implementation:**
```python
# Check submission_date vs due_date
# Status: PENDING → SUBMITTED → GRADED
# Track graded_by and graded_at for audit
```

---

## 🛡️ Security Considerations

### 1. SQL Injection Prevention

- Use Django ORM (parameterized queries)
- Never use raw SQL with user input
- Validate all input data

### 2. XSS Prevention

- Escape HTML in user-generated content
- Use Django's template auto-escaping
- Sanitize rich text input

### 3. CSRF Protection

- Enable CSRF middleware
- Include CSRF token in forms
- Exempt only necessary API endpoints

---
