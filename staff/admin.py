from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Teacher, DrivingInstructor, ProductionMaster, Employee


@admin.register(Teacher)
class TeacherAdmin(ImportExportModelAdmin):
    list_display = ('full_name', 'iin', 'school', 'position', 'status', 'needs_info_update', 'created_at')
    list_filter = ('status', 'position', 'needs_info_update', 'school')
    search_fields = ('last_name', 'first_name', 'middle_name', 'iin', 'school__name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('teaching_categories',)
    
    fieldsets = (
        ('Личные данные', {
            'fields': ('last_name', 'first_name', 'middle_name', 'iin', 'photo')
        }),
        ('Контакты', {
            'fields': ('phone', 'email')
        }),
        ('Автошкола', {
            'fields': ('school', 'user', 'position')
        }),
        ('Квалификация', {
            'fields': ('qualification_number', 'qualification_issue_date', 'qualification_expiry_date', 'teaching_categories')
        }),
        ('Статус', {
            'fields': ('status', 'needs_info_update', 'notes')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DrivingInstructor)
class DrivingInstructorAdmin(ImportExportModelAdmin):
    list_display = ('full_name', 'iin', 'school', 'position', 'status', 'needs_info_update', 'created_at')
    list_filter = ('status', 'position', 'needs_info_update', 'school')
    search_fields = ('last_name', 'first_name', 'middle_name', 'iin', 'school__name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('license_categories',)
    
    fieldsets = (
        ('Личные данные', {
            'fields': ('last_name', 'first_name', 'middle_name', 'iin', 'photo')
        }),
        ('Контакты', {
            'fields': ('phone', 'email')
        }),
        ('Автошкола', {
            'fields': ('school', 'user', 'position')
        }),
        ('Водительское удостоверение', {
            'fields': ('license_number', 'license_issue_date', 'license_expiry_date', 'license_categories')
        }),
        ('Транспорт', {
            'fields': ('assigned_vehicle',)
        }),
        ('Статус', {
            'fields': ('status', 'needs_info_update', 'notes')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductionMaster)
class ProductionMasterAdmin(ImportExportModelAdmin):
    list_display = ('full_name', 'iin', 'school', 'position', 'status', 'needs_info_update', 'created_at')
    list_filter = ('status', 'position', 'needs_info_update', 'school')
    search_fields = ('last_name', 'first_name', 'middle_name', 'iin', 'school__name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('teaching_categories',)
    
    fieldsets = (
        ('Личные данные', {
            'fields': ('last_name', 'first_name', 'middle_name', 'iin', 'photo')
        }),
        ('Контакты', {
            'fields': ('phone', 'email')
        }),
        ('Автошкола', {
            'fields': ('school', 'user', 'position')
        }),
        ('Квалификация', {
            'fields': ('qualification_number', 'qualification_issue_date', 'qualification_expiry_date', 'teaching_categories')
        }),
        ('Статус', {
            'fields': ('status', 'needs_info_update', 'notes')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    list_display = ('full_name', 'email', 'school', 'position', 'is_active', 'created_at')
    list_filter = ('is_active', 'position', 'school')
    search_fields = ('last_name', 'first_name', 'middle_name', 'email', 'iin', 'school__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Личные данные', {
            'fields': ('last_name', 'first_name', 'middle_name', 'iin')
        }),
        ('Контакты', {
            'fields': ('phone', 'email')
        }),
        ('Автошкола', {
            'fields': ('school', 'user', 'position', 'custom_position')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
