from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import School, SchoolCabinet, Vehicle, CatalogCard, SchoolTransaction, SchoolContract, DrivingCategory
from .forms import SchoolForm, SchoolCabinetForm, VehicleForm, CatalogCardForm
from userconf.models import UserSchoolRole


def get_user_schools(user):
    """Get all schools where user has a role"""
    if user.is_superuser or user.is_platform_admin:
        return School.objects.all()
    return School.objects.filter(user_roles__user=user, user_roles__is_active=True).distinct()


def get_current_school(request):
    """Get current active school from session or first available"""
    school_id = request.session.get('current_school_id')
    user_schools = get_user_schools(request.user)
    
    if school_id:
        school = user_schools.filter(id=school_id).first()
        if school:
            return school
    
    # Default to first school
    school = user_schools.first()
    if school:
        request.session['current_school_id'] = school.id
    return school


def school_required(view_func):
    """Decorator to require a school context"""
    def wrapper(request, *args, **kwargs):
        school = get_current_school(request)
        if not school:
            messages.error(request, 'У вас нет доступа к автошколам')
            return redirect('schools:no_school')
        request.current_school = school
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def no_school(request):
    """Page for users without school access"""
    context = {
        'user': request.user,
    }
    return render(request, 'schools/no_school.html', context)


@login_required
def school_list(request):
    """List all schools available to the user"""
    user_schools = get_user_schools(request.user)
    
    if user_schools.count() == 0:
        # User has no schools - show no_school page
        return redirect('schools:no_school')
    
    if user_schools.count() == 1:
        # If user has access to only one school, redirect to dashboard
        school = user_schools.first()
        request.session['current_school_id'] = school.id
        return redirect('schools:dashboard')
    
    context = {
        'schools': user_schools,
    }
    return render(request, 'schools/school_list.html', context)


@login_required
def switch_school(request, school_id):
    """Switch current active school"""
    user_schools = get_user_schools(request.user)
    school = get_object_or_404(user_schools, id=school_id)
    request.session['current_school_id'] = school.id
    messages.success(request, f'Переключено на: {school.name}')
    return redirect('schools:dashboard')


@login_required
@school_required
def dashboard(request):
    """Main school dashboard"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    # Get statistics
    from students.models import StudentGroup, Student
    
    total_groups = school.groups.count()
    active_groups = school.groups.filter(status__in=['enrolling', 'training']).count()
    total_students = Student.objects.filter(group__school=school).count()
    
    # Get user info
    user = request.user
    user_role = UserSchoolRole.objects.filter(user=user, school=school, is_active=True).first()
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'user_role': user_role,
        'total_groups': total_groups,
        'active_groups': active_groups,
        'total_students': total_students,
    }
    return render(request, 'schools/dashboard.html', context)


@login_required
@school_required
def school_profile(request):
    """School profile/about page"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'categories': school.categories.all(),
    }
    return render(request, 'schools/profile.html', context)


@login_required
@school_required
def school_edit(request):
    """Edit school profile"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    if request.method == 'POST':
        form = SchoolForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные автошколы обновлены')
            return redirect('schools:profile')
    else:
        form = SchoolForm(instance=school)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'all_categories': DrivingCategory.objects.all(),
    }
    return render(request, 'schools/school_edit.html', context)


# Cabinets views
@login_required
@school_required
def cabinets_list(request):
    """List all cabinets"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    status_filter = request.GET.get('status', 'approved')
    
    cabinets = school.cabinets.all()
    if status_filter and status_filter != 'all':
        cabinets = cabinets.filter(approval_status=status_filter)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'cabinets': cabinets,
        'status_filter': status_filter,
    }
    return render(request, 'schools/cabinets_list.html', context)


@login_required
@school_required
def cabinet_add(request):
    """Add new cabinet"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    if request.method == 'POST':
        form = SchoolCabinetForm(request.POST)
        if form.is_valid():
            cabinet = form.save(commit=False)
            cabinet.school = school
            cabinet.save()
            messages.success(request, 'Заявка на новый кабинет отправлена')
            return redirect('schools:cabinets')
    else:
        form = SchoolCabinetForm()
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
    }
    return render(request, 'schools/cabinet_form.html', context)


@login_required
@school_required
def cabinet_edit(request, cabinet_id):
    """Edit cabinet"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    cabinet = get_object_or_404(SchoolCabinet, id=cabinet_id, school=school)
    
    if request.method == 'POST':
        form = SchoolCabinetForm(request.POST, instance=cabinet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Кабинет обновлен')
            return redirect('schools:cabinets')
    else:
        form = SchoolCabinetForm(instance=cabinet)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'cabinet': cabinet,
    }
    return render(request, 'schools/cabinet_form.html', context)


# Vehicles views
@login_required
@school_required
def vehicles_list(request):
    """List all vehicles"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    search = request.GET.get('search', '')
    
    vehicles = school.vehicles.all()
    if search:
        vehicles = vehicles.filter(
            Q(brand__icontains=search) |
            Q(model__icontains=search) |
            Q(plate_number__icontains=search)
        )
    
    paginator = Paginator(vehicles, 20)
    page = request.GET.get('page', 1)
    vehicles = paginator.get_page(page)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'vehicles': vehicles,
        'search': search,
    }
    return render(request, 'schools/vehicles_list.html', context)


@login_required
@school_required
def vehicle_add(request):
    """Add new vehicle"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.school = school
            vehicle.save()
            messages.success(request, 'Транспортное средство добавлено')
            return redirect('schools:vehicles')
    else:
        form = VehicleForm()
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'categories': DrivingCategory.objects.all(),
    }
    return render(request, 'schools/vehicle_form.html', context)


@login_required
@school_required
def vehicle_edit(request, vehicle_id):
    """Edit vehicle"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, school=school)
    
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Транспортное средство обновлено')
            return redirect('schools:vehicles')
    else:
        form = VehicleForm(instance=vehicle)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'vehicle': vehicle,
        'categories': DrivingCategory.objects.all(),
    }
    return render(request, 'schools/vehicle_form.html', context)


@login_required
@school_required
@require_POST
def vehicle_delete(request, vehicle_id):
    """Delete vehicle"""
    school = request.current_school
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, school=school)
    vehicle.delete()
    messages.success(request, 'Транспортное средство удалено')
    return redirect('schools:vehicles')


# Catalog cards views
@login_required
@school_required
def catalog_cards_list(request):
    """List catalog cards"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    status_filter = request.GET.get('status', 'active')
    
    cards = school.catalog_cards.all()
    if status_filter and status_filter != 'all':
        cards = cards.filter(status=status_filter)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'cards': cards,
        'status_filter': status_filter,
    }
    return render(request, 'schools/catalog_cards_list.html', context)


@login_required
@school_required
def catalog_card_add(request):
    """Add catalog card"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    if request.method == 'POST':
        form = CatalogCardForm(request.POST, request.FILES)
        if form.is_valid():
            card = form.save(commit=False)
            card.school = school
            card.save()
            messages.success(request, 'Карточка добавлена в каталог')
            return redirect('schools:catalog_cards')
    else:
        form = CatalogCardForm()
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'categories': DrivingCategory.objects.all(),
    }
    return render(request, 'schools/catalog_card_form.html', context)


@login_required
@school_required
def catalog_card_edit(request, card_id):
    """Edit catalog card"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    card = get_object_or_404(CatalogCard, id=card_id, school=school)
    
    if request.method == 'POST':
        form = CatalogCardForm(request.POST, request.FILES, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, 'Карточка обновлена')
            return redirect('schools:catalog_cards')
    else:
        form = CatalogCardForm(instance=card)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'card': card,
        'categories': DrivingCategory.objects.all(),
    }
    return render(request, 'schools/catalog_card_form.html', context)


@login_required
@school_required
def catalog_card_toggle(request, card_id):
    """Toggle catalog card active status"""
    school = request.current_school
    card = get_object_or_404(CatalogCard, id=card_id, school=school)
    card.is_active = not card.is_active
    card.save()
    status = 'активирована' if card.is_active else 'деактивирована'
    messages.success(request, f'Карточка {status}')
    return redirect('schools:catalog_cards')


# Transactions views
@login_required
@school_required
def transactions_list(request):
    """List school transactions"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    transactions = school.transactions.all()
    
    paginator = Paginator(transactions, 20)
    page = request.GET.get('page', 1)
    transactions = paginator.get_page(page)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'transactions': transactions,
    }
    return render(request, 'schools/transactions_list.html', context)


# Contracts views
@login_required
@school_required
def contracts_list(request):
    """List school contracts"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    # Check if contracts module is active
    has_active_contract = school.contracts.filter(is_active=True).exists()
    
    contracts = school.contracts.all()
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'contracts': contracts,
        'has_active_contract': has_active_contract,
    }
    return render(request, 'schools/contracts_list.html', context)
