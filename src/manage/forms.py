from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from . models import User, StudentProfile, TeacherProfile

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'role', 'first_name', 'last_name', 'password1', 'password2']
    

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['roll_no', 'section', 'date_of_birth']
    

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['department', 'designation', 'qualification','description']


class CustomAuthenticationForm(AuthenticationForm):
    username_field = "email"
    fields = ('username', 'password')