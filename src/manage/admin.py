from django.contrib import admin
from . models import User, StudentProfile, TeacherProfile, Section, Subject, TeachingAssignment, Assignment, Submission, Semester, Course, Batch


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("first_name","last_name", "email", "role")
    list_filter = ('id',)
    search_fields = ('first_name', 'id')

@admin.register(StudentProfile)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user__id", "user__first_name","user__last_name", "section__semester", "section__name", "roll_no")
    list_filter = ("section",)
    search_fields = ("user__email", "user__id")


@admin.register(TeacherProfile)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("user__id", "user__first_name", "department")
    list_filter = ("department",)
    search_fields = ("user__email", "user__id")


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("name", "semester", "batch","course","branch")
    search_fields = ("name",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "description")
    search_fields = ("subject_code",)

@admin.register(TeachingAssignment)
class SectionSubjectTeacherAdmin(admin.ModelAdmin):
    list_display = ("section", "subject", "teacher")
    list_filter = ("section", "teacher")
    search_fields = ("subject__subject_name", "teacher__user__email")


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("assignment_id", "section_subject_teacher", "title", "due_date")
    list_filter = ("section_subject_teacher__section",)
    search_fields = ("title",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("submission_id", "assignment", "student")
    list_filter = ("assignment", "student")
    search_fields = ("student__user__email", "assignment__title")

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    model = Semester

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    model = Course

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    model = Batch