from django.shortcuts import redirect, render
from .forms import CustomUserCreationForm, TeacherProfileForm, StudentProfileForm, LoginForm
from django.contrib.auth import login, authenticate
from .models import User, StudentProfile, TeachingAssignment


def homeview(request):
    context = {}
    return render(request, "manage/index.html", context=context)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            return redirect('student_dashboard')
        else:
            form.add_error(None, "Invalid email or password")

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('student_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form' : form})            


def profile_view(request):
    if request.method == 'POST':
        if request.user.role == User.STUDENT:
            form = StudentProfileForm(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                return redirect('home')
        elif request.user.role == User.TEACHER:
            form = TeacherProfileForm(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                return redirect('home')
    else:
        form = StudentProfileForm() if request.user.role == User.STUDENT else TeacherProfileForm()
    return render(request, 'registration/profile.html', {'form': form})
    
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User, StudentProfile, Subject, Assignment


@login_required
def dashboard_view(request):
    user = request.user

    if user.role == User.STUDENT:
        student = StudentProfile.objects.filter(user=user).first()
        teachingAssignment = TeachingAssignment.objects.filter(section=student.section, batch=student.batch, course=student.course)
        
        context = {
            'student': student,
            'section': teachingAssignment.section,
            'subjects' : teachingAssignment.subject,
            'teacher' : teachingAssignment.teacher
        }
        return render(request, 'manage/student_dashboard.html', context)

    return redirect('home')

