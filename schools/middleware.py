from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class SchoolContextMiddleware:
    """Middleware to set current school context for authenticated users"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Skip for admin and static paths
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return self.get_response(request)
        
        # Set current school if user has school roles
        if hasattr(request.user, 'school_roles'):
            school_id = request.session.get('current_school_id')
            
            if school_id:
                from schools.models import School
                try:
                    if request.user.is_superuser or request.user.is_platform_admin:
                        school = School.objects.get(id=school_id)
                    else:
                        school = School.objects.filter(
                            id=school_id,
                            user_roles__user=request.user,
                            user_roles__is_active=True
                        ).first()
                    
                    if school:
                        request.current_school = school
                except School.DoesNotExist:
                    pass
        
        return self.get_response(request)


class RoleRequiredMixin:
    """Mixin to require specific roles for class-based views"""
    required_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login:login_view')
        
        # Superusers and platform admins bypass role checks
        if request.user.is_superuser or request.user.is_platform_admin:
            return super().dispatch(request, *args, **kwargs)
        
        # Check if user has required role
        if self.required_roles:
            from userconf.models import UserSchoolRole
            has_role = UserSchoolRole.objects.filter(
                user=request.user,
                role__code__in=self.required_roles,
                is_active=True
            ).exists()
            
            if not has_role:
                messages.error(request, 'У вас нет доступа к этой странице')
                return redirect('schools:dashboard')
        
        return super().dispatch(request, *args, **kwargs)

