from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    DrivingCategory, School, SchoolCabinet, Vehicle,
    CatalogCard, SchoolTransaction, SchoolContract
)


@admin.register(DrivingCategory)
class DrivingCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name')
    ordering = ('code',)


class SchoolCabinetInline(admin.TabularInline):
    model = SchoolCabinet
    extra = 0
    fields = ('address', 'approval_status', 'created_at')
    readonly_fields = ('created_at',)


class VehicleInline(admin.TabularInline):
    model = Vehicle
    extra = 0
    fields = ('brand', 'model', 'plate_number', 'category', 'status')


@admin.register(School)
class SchoolAdmin(ImportExportModelAdmin):
    list_display = ('name', 'bin_iin', 'director_full_name', 'phone', 'is_active', 'is_verified', 'created_at')
    list_filter = ('is_active', 'is_verified', 'categories', 'created_at')
    search_fields = ('name', 'bin_iin', 'director_full_name', 'director_iin', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('categories',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'short_name', 'bin_iin', 'logo')
        }),
        ('Директор', {
            'fields': ('director_full_name', 'director_iin')
        }),
        ('Контактная информация', {
            'fields': ('address', 'phone', 'email')
        }),
        ('Лицензия', {
            'fields': ('license_number', 'license_issue_date', 'license_expiry_date')
        }),
        ('Категории и настройки', {
            'fields': ('categories', 'allow_electronic_certificates')
        }),
        ('Финансы', {
            'fields': ('balance', 'cashback_certificate_percent', 'cashback_aitest_percent')
        }),
        ('Статус', {
            'fields': ('is_active', 'is_verified')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [SchoolCabinetInline, VehicleInline]


@admin.register(SchoolCabinet)
class SchoolCabinetAdmin(admin.ModelAdmin):
    list_display = ('school', 'address', 'approval_status', 'created_at')
    list_filter = ('approval_status', 'school')
    search_fields = ('address', 'school__name')
    readonly_fields = ('created_at', 'approved_at')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'plate_number', 'school', 'category', 'transmission', 'status', 'created_at')
    list_filter = ('status', 'category', 'transmission', 'school')
    search_fields = ('brand', 'model', 'plate_number', 'school__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CatalogCard)
class CatalogCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'category', 'status', 'is_active', 'created_at')
    list_filter = ('status', 'is_active', 'category', 'school')
    search_fields = ('name', 'school__name', 'address')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SchoolTransaction)
class SchoolTransactionAdmin(admin.ModelAdmin):
    list_display = ('school', 'amount', 'transaction_type', 'user', 'created_at')
    list_filter = ('transaction_type', 'school', 'created_at')
    search_fields = ('school__name', 'description')
    readonly_fields = ('created_at', 'balance_before', 'balance_after')
    date_hierarchy = 'created_at'


@admin.register(SchoolContract)
class SchoolContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'school', 'title', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'school', 'start_date')
    search_fields = ('contract_number', 'title', 'school__name')
    readonly_fields = ('created_at', 'updated_at')
