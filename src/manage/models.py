from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from learnflow import settings
# Create your models here.


class CustomUserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    ADMIN = "ADMIN"

    ROLE_CHOICE = [
        (STUDENT, "Student"),
        (TEACHER, "Teacher"),
        (ADMIN, "Admin"),
    ]

    username = None  # REMOVE the default username field
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICE, default=STUDENT)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # no username required

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"


class Course(models.Model):
    COURSES = [
        ("B.Tech.", "Batchleors of technology"),
        ("BCA", "Batchleors in computer applications"),
        ("BBA", "Batchleors in Business Adminstration"),
        ("M.Tech.", "Masters of technology"),
        ("EEE", "Electrical and Electronics Engineering"),
    ]
    name = models.CharField(max_length=20,unique=True, choices=COURSES) # B.Tech
    def __str__(self):
        return self.get_name_display()


class Batch(models.Model):
    batch = models.CharField(max_length=4, primary_key=True)

    def save(self, *args, **kwargs):
        if not self.batch.isnumeric():
            raise ValidationError("Batch must be a Year, eg., 2027")
        super().save(*args, **kwargs)


class Semester(models.Model):
    semester = models.PositiveSmallIntegerField(choices=[(i, f"Semester {i}") for i in range(1,9)])
    
    def __str__(self):
        return self.get_semester_display()
    

class Subject(models.Model):
    code = models.CharField(unique=True, primary_key=True, blank=False, max_length=6)
    title = models.TextField(blank=True)
    description = models.FileField(blank=True, null=True)
    syllabus = models.TextField(blank=True, null=True)
    semester = models.ForeignKey(
        Semester,
        on_delete = models.CASCADE,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ['course', 'code', 'semester']


    def __str__(self):
        return f"{self.subject_code} - ({self.description})"
    

class Section(models.Model):
    name = models.CharField(max_length=5, primary_key=True, unique=True)
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE
    ) 
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True
    )

    BRANCHES = {
        "B.Tech.": [
            ("CSE", "Computer Science and Engineering"),
            ("ME", "Mechanical Engineering"),
            ("CE", "Civil Engineering"),
            ("EE", "Electrical Engineering"),
            ("ECE", "Electronics Engineering"),
            ("EEE", "Electrical and Electronics Engineering"),
        ],
        "M.Tech.": [
            ("AI", "Artificial Intelligence"),
            ("DS", "Data Science"),
        ],
    }
    branch = models.CharField(
        max_length=5,
        choices=BRANCHES,
        blank=False
    )
    class Meta:
        unique_together = ("name", "semester", "course", "branch")


class StudentProfile(models.Model):
    """Extended profile for students"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'}, related_name='student_profile')
    roll_no = models.CharField(max_length=50, unique=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, related_name='students')
    date_of_birth = models.DateField(null=True, blank=True)
    enrollment_date = models.DateField(default=timezone.now)
    
    class Meta: 
        unique_together = ['section', 'roll_no']
    
    def __str__(self):
        return f"{self.roll_no} - {self.user.get_full_name()}"


class TeacherProfile(models.Model):
    """Extended profile for teachers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'TEACHER'}, related_name='teacher_profile')
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    
    class Meta:
        db_table = 'teacher_profiles'
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"


class TeachingAssignment(models.Model):
    """Junction Table matching section, subject and teacher"""
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        related_name='section_subjects',
    )

    subject = models.ForeignKey(
        Subject,
        on_delete= models.SET_NULL,
        null=True,
        related_name="teaching_assingments"
    )

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='taught_by'
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ['section', 'subject', 'batch']
        verbose_name = 'Section-Subject-Teacher Mapping'
        verbose_name_plural = 'Section-Subject-Teacher Mappings'

    
class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    section_subject_teacher = models.ForeignKey(
        TeachingAssignment,
        on_delete=models.CASCADE,
        related_name='issued_by'
    )
    title = models.CharField(max_length=10, blank=False)
    descreption = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField()
    max_marks = models.IntegerField(default=100)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} Due_by {self.due_date}"

    def is_overdue(self):
        return timezone.now() > self.due_date

    @property
    def section(self):
        return self.section_subject_teacher.section
    
    @property
    def subject(self):
        return self.section_subject_teacher.subject

    @property
    def teacher(self):
        return self.section_subject_teacher.teacher


class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submission'
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='submitted_by'
    )
    file_link = models.FileField(upload_to='submissions/%Y/%m/%d/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.IntegerField(blank=True, null=True)


    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.name} - {self.assignment.title} - {self.submitted_at}"

    def clean(self):
        # check if the student is not belongs to the assingment section
        if self.student.section != self.assignment.section:
            raise ValidationError({
                'student':'You are not belongs this section, Spoofer'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_late(self):
        return self.submitted_at > self.assignment.due_date