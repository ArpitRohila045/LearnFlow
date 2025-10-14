from django.urls import path
from . import views
from pathlib import Path

print("urlpatterns in : ", Path(__file__).resolve().parent.parent)

urlpatterns = [
    path('', views.homeview, name='homeview'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/profile/', views.profile_view, name='signup_profile'),
]