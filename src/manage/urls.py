from django.urls import path
from . import views
from pathlib import Path

print("urlpatterns in : ", Path(__file__).resolve().parent.parent)

urlpatterns = [
    path('', views.homeview, name='homeview'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('signup/profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='student_dashboard'),
    path('logout/', views.logout_view, name='logout')
]