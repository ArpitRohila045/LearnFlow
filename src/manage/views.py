from django.shortcuts import redirect, render
from .forms import CustomUserCreationForm, TeacherProfileForm, StudentProfileForm, LoginForm
from django.contrib.auth import login, authenticate, logout
from .models import User, StudentProfile, TeachingAssignment, TeacherProfile
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User, StudentProfile, Subject, Assignment, Section
from django.http import JsonResponse
from django.forms import modelformset_factory



def get_subjects(request):
    course_id = request.GET.get('course')
    semester_id = request.GET.get('semester')

    subjects = Subject.objects.filter(course_id=course_id, semester_id=semester_id)

    data = [{"id": s.id, "code": s.code, "title": s.title} for s in subjects]
    return JsonResponse({"subjects": data})



def get_sections(request):
    course_id = request.GET.get('course')
    batch = request.GET.get('batch')
    semester_id = request.GET.get('semester')

    sections = Section.objects.filter(course_id=course_id, batch_id=batch, semester_id=semester_id)

    data = [{"id": sec.id, "name": sec.name} for sec in sections]   # changed sec.name -> sec.id
    return JsonResponse({"sections": data})



def homeview(request):
    context = {}
    return render(request, "manage/index.html", context=context)


def login_view(request):
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Check if profile exists
                if user.role == User.STUDENT:
                    if hasattr(user, 'student_profile'):
                        return redirect('dashboard_view')
                    else:
                        return redirect('profile')
                
                elif user.role == User.TEACHER:
                    if hasattr(user, 'teacher_profile'):
                        return redirect('dashboard_view')
                    else:
                        return redirect('profile')
                
                else:
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
    if flag:
        return redirect(dashboardSelector(request.user))

    AssignmentFormSet = modelformset_factory(
        TeachingAssignment,
        fields=("course", "batch", "semester", "section", "subject"),
        extra=1,
        can_delete=True
    )

    if request.method == 'POST':
        if request.user.role == User.TEACHER:
            profile_form = TeacherProfileForm(request.POST)
            formset = AssignmentFormSet(request.POST)

            if profile_form.is_valid() and formset.is_valid():
                profile = profile_form.save(commit=False)
                profile.user = request.user
                profile.save()

                formset.save()
                return redirect('homeview')
        else:
            profile_form = StudentProfileForm(request.POST)
            if profile_form.is_valid():
                p = profile_form.save(commit=False)
                p.user = request.user
                p.save()
                return redirect('student_dashboard')
    else:
        profile_form = StudentProfileForm() if request.user.role == User.STUDENT else TeacherProfileForm()
        formset = AssignmentFormSet(queryset=TeachingAssignment.objects.none())

    return render(request, 'registration/profile.html', {
        'form': profile_form,
        'formset': formset
    })



@login_required
def dashboard_view(request):
    user = request.user

    if user.role == User.STUDENT:
        context = student_dashboard_view(user)
        return render(request, 'manage/student_dashboard.html', context)

    elif user.role == User.TEACHER:
        if not hasattr(user, 'teacher_profile'):
            return redirect('profile')
        context = teacher_dashboard_view(user)
        return render(request, 'manage/teacher_dashboard.html', context)

    return redirect('homeview')



@login_required
def logout_view(request):
    if request.method == "POST": 
        logout(request)
        return redirect('homeview')
    return redirect('homeview')



@login_required
def teacherProfile(request, teacher_id):    
    teacher = get_object_or_404(TeacherProfile, id=teacher_id)
    return render(request, 'manage/teacher_profile.html', {'teacher' : teacher})



def teacher_dashboard_view(user):
    """Return context dict for teacher dashboard (never performs redirects)."""
    teacher = getattr(user, 'teacher_profile', None)
    if not teacher:
        return {}  # dashboard_view handles redirect when profile missing

    teaching_assignments = TeachingAssignment.objects.filter(teacher=teacher).select_related('section', 'subject')

    # get distinct Section and Subject objects referenced by these assignments
    section_ids = teaching_assignments.values_list('section_id', flat=True).distinct()
    subject_ids = teaching_assignments.values_list('subject_id', flat=True).distinct()

    sections = Section.objects.filter(id__in=section_ids)
    subjects = Subject.objects.filter(id__in=subject_ids)

    context = {
        'teacher': teacher,
        'teaching_assignments': teaching_assignments,
        'sections': sections,
        'subjects': subjects,
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