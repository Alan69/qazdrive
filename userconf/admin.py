from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserRole, UserSchoolRole, AuthLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'phone_number', 'full_name', 'email', 'iin', 'city', 'is_platform_admin', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_platform_admin', 'city')
    search_fields = ('phone_number', 'first_name', 'last_name', 'email', 'iin')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Учетные данные', {
            'fields': ('phone_number', 'password')
        }),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'middle_name', 'iin', 'email', 'city', 'avatar')
        }),
        ('Тарифы и подписки', {
            'fields': ('category', 'is_have_tarif', 'is_subscribed', 'tarif_name', 'tarif_expire_date', 'pddtest_pass')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_platform_admin', 'groups', 'user_permissions')
        }),
        ('Важные даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name')


@admin.register(UserSchoolRole)
class UserSchoolRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'role', 'is_active', 'assigned_at')
    list_filter = ('role', 'is_active', 'school')
    search_fields = ('user__phone_number', 'user__first_name', 'user__last_name', 'school__name')
    raw_id_fields = ('user', 'school')


@admin.register(AuthLog)
class AuthLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'ip_address', 'is_successful', 'logout_time')
    list_filter = ('is_successful', 'login_time')
    search_fields = ('user__phone_number', 'user__first_name', 'ip_address')
    readonly_fields = ('user', 'login_time', 'ip_address', 'user_agent', 'is_successful')
    date_hierarchy = 'login_time'
