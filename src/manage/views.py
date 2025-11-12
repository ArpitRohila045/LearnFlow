from django.shortcuts import redirect, render
from .forms import CustomUserCreationForm, TeacherProfileForm, StudentProfileForm, LoginForm
from django.contrib.auth import login, authenticate, logout
from .models import User, StudentProfile, TeachingAssignment



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



def profile_view(request):
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



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User, StudentProfile, Subject, Assignment



@login_required
def dashboard_view(request):
    user = request.user

    if user.role == User.STUDENT:
        student = StudentProfile.objects.filter(user=user).first()
        if not student:
            return redirect('profile')
        teachingAssignment = TeachingAssignment.objects.filter(section=student.section, batch=student.batch, course=student.course)
        
        context = {
            'student': student,
            'section': teachingAssignment.values('section'),
            'subjects': teachingAssignment.values('subject'),
            'teacher': teachingAssignment.values('teacher')
        }
        return render(request, 'manage/student_dashboard.html', context)

    elif user.role == User.TEACHER:
        return redirect('teacher_dashboard')  # Ensure this URL exists

    return redirect('home')



@login_required
def logout_view(request):
    if request.method == "POST" or request.method == "GET":  # allow both
        logout(request)
        return redirect('homeview')
    return redirect('homeview')
