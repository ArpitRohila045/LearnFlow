from django.shortcuts import redirect, render, HttpResponse
from .forms import CustomUserCreationForm, CustomAuthenticationForm, TeacherProfileForm, StudentProfileForm
from django.contrib.auth import login
from .models import User


def homeview(request):
    context = {}
    return render(request, "base.html", context=context)

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('signup_profile')
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
    