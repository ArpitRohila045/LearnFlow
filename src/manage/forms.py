from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from . models import User, StudentProfile, TeacherProfile

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'role', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Removing password-based authentication
        if 'usable_password' in self.fields:
          del self.fields['usable_password']

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['batch' ,'course', 'section', 'roll_no', 'semester']
    

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['department', 'designation', 'qualification','description']


class CustomAuthenticationForm(AuthenticationForm):
    username_field = "email"
    fields = ('username', 'password')

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)