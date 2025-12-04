from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """
    Decorator to require specific user roles.
    Usage: @role_required('school_director', 'school_manager')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login:login_view')
            
            # Superusers and platform admins bypass role checks
            if request.user.is_superuser or request.user.is_platform_admin:
                return view_func(request, *args, **kwargs)
            
            # Check if user has any of the required roles
            from userconf.models import UserSchoolRole
            has_role = UserSchoolRole.objects.filter(
                user=request.user,
                role__code__in=roles,
                is_active=True
            ).exists()
            
            if not has_role:
                messages.error(request, 'У вас нет доступа к этой странице')
                return redirect('schools:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def school_director_required(view_func):
    """Decorator to require school director role"""
    return role_required('school_director', 'platform_admin')(view_func)


def school_manager_required(view_func):
    """Decorator to require school manager or director role"""
    return role_required('school_director', 'school_manager', 'platform_admin')(view_func)


def staff_required(view_func):
    """Decorator to require any staff role"""
    return role_required(
        'school_director', 'school_manager', 'teacher',
        'driving_instructor', 'production_master', 'employee', 'platform_admin'
    )(view_func)


def platform_admin_required(view_func):
    """Decorator to require platform admin role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login:login_view')
        
        if not (request.user.is_superuser or request.user.is_platform_admin):
            messages.error(request, 'Доступ запрещен')
            return redirect('schools:dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper

