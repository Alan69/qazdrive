from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST

from .models import Teacher, DrivingInstructor, ProductionMaster, Employee
from .forms import TeacherForm, DrivingInstructorForm, ProductionMasterForm, EmployeeForm
from schools.views import get_user_schools, get_current_school, school_required
from schools.models import DrivingCategory


# Teachers views
@login_required
@school_required
def teachers_list(request):
    """List all teachers"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    status_filter = request.GET.get('status', 'active')
    search = request.GET.get('search', '')
    
    teachers = Teacher.objects.filter(school=school)
    
    if status_filter == 'active':
        teachers = teachers.filter(status='active')
    elif status_filter == 'archived':
        teachers = teachers.filter(status='archived')
    
    if search:
        teachers = teachers.filter(
            Q(last_name__icontains=search) |
            Q(first_name__icontains=search) |
            Q(iin__icontains=search)
        )
    
    teachers = teachers.order_by('-created_at')
    
    paginator = Paginator(teachers, 20)
    page = request.GET.get('page', 1)
    teachers = paginator.get_page(page)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'teachers': teachers,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'staff/teachers_list.html', context)


@login_required
@school_required
def teacher_add(request):
    """Add new teacher"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save(commit=False)
            teacher.school = school
            teacher.save()
            form.save_m2m()
            messages.success(request, 'Преподаватель добавлен')
            return redirect('staff:teachers')
    else:
        form = TeacherForm()
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'categories': DrivingCategory.objects.all(),
    }
    return render(request, 'staff/teacher_form.html', context)


@login_required
@school_required
def teacher_edit(request, teacher_id):
    """Edit teacher"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    teacher = get_object_or_404(Teacher, id=teacher_id, school=school)
    
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные преподавателя обновлены')
            return redirect('staff:teachers')
    else:
        form = TeacherForm(instance=teacher)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'teacher': teacher,
        'categories': DrivingCategory.objects.all(),
    }
    return render(request, 'staff/teacher_form.html', context)


# Driving Instructors views
@login_required
@school_required
def drivers_list(request):
    """List all driving instructors"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    status_filter = request.GET.get('status', 'active')
    search = request.GET.get('search', '')
    
    instructors = DrivingInstructor.objects.filter(school=school)
    
    if status_filter == 'active':
        instructors = instructors.filter(status='active')
    elif status_filter == 'archived':
        instructors = instructors.filter(status='archived')
    
    if search:
        instructors = instructors.filter(
            Q(last_name__icontains=search) |
            Q(first_name__icontains=search) |
            Q(iin__icontains=search)
        )
    
    instructors = instructors.order_by('-created_at')
    
    paginator = Paginator(instructors, 20)
    page = request.GET.get('page', 1)
    instructors = paginator.get_page(page)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'instructors': instructors,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'staff/drivers_list.html', context)


@login_required
@school_required
def driver_add(request):
    """Add new driving instructor"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    if request.method == 'POST':
        form = DrivingInstructorForm(request.POST, request.FILES, school=school)
        if form.is_valid():
            instructor = form.save(commit=False)
            instructor.school = school
            instructor.save()
            form.save_m2m()
            messages.success(request, 'Мастер обучения вождению добавлен')
            return redirect('staff:drivers')
    else:
        form = DrivingInstructorForm(school=school)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'categories': DrivingCategory.objects.all(),
    }
    return render(request, 'staff/driver_form.html', context)


@login_required
@school_required
def driver_edit(request, driver_id):
    """Edit driving instructor"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    instructor = get_object_or_404(DrivingInstructor, id=driver_id, school=school)
    
    if request.method == 'POST':
        form = DrivingInstructorForm(request.POST, request.FILES, instance=instructor, school=school)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные мастера обновлены')
            return redirect('staff:drivers')
    else:
        form = DrivingInstructorForm(instance=instructor, school=school)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'instructor': instructor,
        'categories': DrivingCategory.objects.all(),
    }
    return render(request, 'staff/driver_form.html', context)


# Production Masters views
@login_required
@school_required
def masters_list(request):
    """List all production masters"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    status_filter = request.GET.get('status', 'active')
    search = request.GET.get('search', '')
    
    masters = ProductionMaster.objects.filter(school=school)
    
    if status_filter == 'active':
        masters = masters.filter(status='active')
    elif status_filter == 'archived':
        masters = masters.filter(status='archived')
    
    if search:
        masters = masters.filter(
            Q(last_name__icontains=search) |
            Q(first_name__icontains=search) |
            Q(iin__icontains=search)
        )
    
    masters = masters.order_by('-created_at')
    
    paginator = Paginator(masters, 20)
    page = request.GET.get('page', 1)
    masters = paginator.get_page(page)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'masters': masters,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'staff/masters_list.html', context)


@login_required
@school_required
def master_add(request):
    """Add new production master"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    if request.method == 'POST':
        form = ProductionMasterForm(request.POST, request.FILES)
        if form.is_valid():
            master = form.save(commit=False)
            master.school = school
            master.save()
            form.save_m2m()
            messages.success(request, 'Мастер производственного обучения добавлен')
            return redirect('staff:masters')
    else:
        form = ProductionMasterForm()
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'categories': DrivingCategory.objects.all(),
    }
    return render(request, 'staff/master_form.html', context)


@login_required
@school_required
def master_edit(request, master_id):
    """Edit production master"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    master = get_object_or_404(ProductionMaster, id=master_id, school=school)
    
    if request.method == 'POST':
        form = ProductionMasterForm(request.POST, request.FILES, instance=master)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные мастера обновлены')
            return redirect('staff:masters')
    else:
        form = ProductionMasterForm(instance=master)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'master': master,
        'categories': DrivingCategory.objects.all(),
    }
    return render(request, 'staff/master_form.html', context)


# Employees views
@login_required
@school_required
def workers_list(request):
    """List all employees"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    employees = Employee.objects.filter(school=school).order_by('-created_at')
    
    paginator = Paginator(employees, 20)
    page = request.GET.get('page', 1)
    employees = paginator.get_page(page)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'employees': employees,
    }
    return render(request, 'staff/workers_list.html', context)


@login_required
@school_required
def worker_add(request):
    """Add new employee"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.school = school
            employee.save()
            messages.success(request, 'Сотрудник добавлен')
            return redirect('staff:workers')
    else:
        form = EmployeeForm()
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
    }
    return render(request, 'staff/worker_form.html', context)


@login_required
@school_required
def worker_edit(request, worker_id):
    """Edit employee"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    employee = get_object_or_404(Employee, id=worker_id, school=school)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные сотрудника обновлены')
            return redirect('staff:workers')
    else:
        form = EmployeeForm(instance=employee)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'employee': employee,
    }
    return render(request, 'staff/worker_form.html', context)
