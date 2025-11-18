from django.urls import path
from . import views
from pathlib import Path

print("urlpatterns in : ", Path(__file__).resolve().parent.parent)

urlpatterns = [
    path('', views.homeview, name='homeview'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard_view'),
    # path('student/<int:student_id>', views.studentProfile, name='teacher_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('teacher/<int:teacher_id>', views.teacherProfile, name='teacher_profile'),
    path("ajax/subjects/", views.get_subjects, name="ajax_get_subjects"),
    path("ajax/sections/", views.get_sections, name="ajax_get_sections"),
]