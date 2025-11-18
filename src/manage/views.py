from django.shortcuts import redirect, render
from .forms import CustomUserCreationForm, TeacherProfileForm, StudentProfileForm, LoginForm
from django.contrib.auth import login, authenticate, logout
from .models import User, StudentProfile, TeachingAssignment, TeacherProfile
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User, StudentProfile, Subject, Assignment




def homeview(request):
    context = {}
    return render(request, "manage/index.html", context=context)



def login_view(request):
    print("Login View Accessed")
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                if user.role == user.STUDENT:
                    return redirect('student_dashboard')
                elif user.role == user.TEACHER:
                    return redirect('teacher_dashboard')
                else:
                    print("unknow role")
                    return redirect('homeview')
            else:
                form.add_error(None, "Invalid email or password")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})



def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form' : form})            


def dashboardSelector(user):
    if user.role == User.STUDENT:
        return 'student_dashboard'
    elif user.role == User.TEACHER:
        return 'teacher_dashboard'
    else:
        return 'homeview'


def profile_view(request):
    flag = hasattr(request.user, "student_profile") or hasattr(request.user, "teacher_profile")
    print(flag)
    # print(request.user.student_profile)
    if flag:
        return redirect(dashboardSelector(request.user))
    
    if request.method == 'POST':
        if request.user.role == User.STUDENT:
            form = StudentProfileForm(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                return redirect('student_dashboard')
        elif request.user.role == User.TEACHER:
            form = TeacherProfileForm(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                return redirect('homeview')
    else:
        form = StudentProfileForm() if request.user.role == User.STUDENT else TeacherProfileForm()
    return render(request, 'registration/profile.html', {'form': form})



@login_required
def dashboard_view(request):
    user = request.user

    if user.role == User.STUDENT:
        context = student_dashboard_view(user)
        return render(request, 'manage/student_dashboard.html', context)

    elif user.role == User.TEACHER:
        context = teacher_dashboard_view(user)
        return render(request, 'manage/teacher_dashboard', context)  # Ensure this URL exists

    return redirect('home')



@login_required
def logout_view(request):
    if request.method == "POST" or request.method == "GET":  # allow both
        logout(request)
        return redirect('homeview')
    return redirect('homeview')



@login_required
def teacherProfile(request, teacher_id):    
    teacher = get_object_or_404(TeacherProfile, id=teacher_id)
    return render(request, 'manage/teacher_profile.html', {'teacher' : teacher})



def teacher_dashboard_view(user):
    teaching_assignments = TeachingAssignment.objects.filter(teacher = user.teacher_profile)
    context = {
        'sections' : teaching_assignments.section.all(),
        'subjects' : teaching_assignments.subject.all()
    }
    return context



def student_dashboard_view(user):
    student = StudentProfile.objects.filter(user=user).first()
    if not student:
        return redirect('profile')
    
    teachingAssignment = TeachingAssignment.objects.filter(section=student.section, batch=student.batch, course=student.course)
    subject_list = [
        {
            'subject': ta.subject.title,
            'teacher': ta.teacher.user.get_full_name(),
            'teacher_id' : ta.teacher.id,
        }   
        for ta in teachingAssignment 
    ]
    context = {
        'student': student,
        'subject_list' : subject_list,
    }

    return context