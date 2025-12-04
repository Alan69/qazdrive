from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Certificate, CertificateVerification, CertificateTemplate


class CertificateVerificationInline(admin.TabularInline):
    model = CertificateVerification
    extra = 0
    fields = ('verified_by', 'verified_at', 'ip_address', 'is_valid')
    readonly_fields = ('verified_at',)


@admin.register(Certificate)
class CertificateAdmin(ImportExportModelAdmin):
    list_display = ('certificate_number', 'student', 'school', 'category', 'status', 'issue_date', 'is_valid')
    list_filter = ('status', 'category', 'school', 'issue_date')
    search_fields = ('certificate_number', 'student__last_name', 'student__first_name', 'student__iin', 'school__name')
    readonly_fields = ('uuid', 'created_at', 'updated_at', 'is_valid', 'verification_url')
    
    fieldsets = (
        ('Идентификация', {
            'fields': ('uuid', 'certificate_number')
        }),
        ('Курсант и школа', {
            'fields': ('student', 'school', 'category')
        }),
        ('Даты', {
            'fields': ('issue_date', 'expiry_date', 'training_start_date', 'training_end_date')
        }),
        ('Обучение', {
            'fields': ('theory_hours', 'practice_hours', 'theory_exam_passed', 'practice_exam_passed')
        }),
        ('Файлы', {
            'fields': ('qr_code', 'pdf_file')
        }),
        ('Статус', {
            'fields': ('status', 'issued_by', 'notes')
        }),
        ('Отзыв', {
            'fields': ('revocation_reason', 'revoked_at', 'revoked_by'),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('is_valid', 'verification_url', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [CertificateVerificationInline]
    
    def is_valid(self, obj):
        return obj.is_valid
    is_valid.boolean = True
    is_valid.short_description = 'Действителен'
    
    def verification_url(self, obj):
        return obj.verification_url
    verification_url.short_description = 'URL верификации'


@admin.register(CertificateVerification)
class CertificateVerificationAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'verified_by', 'verified_at', 'ip_address', 'is_valid')
    list_filter = ('is_valid', 'verified_at')
    search_fields = ('certificate__certificate_number', 'certificate__student__last_name', 'ip_address')
    readonly_fields = ('verified_at',)
    date_hierarchy = 'verified_at'


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'school', 'is_default', 'is_active')
    list_filter = ('is_default', 'is_active', 'category', 'school')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
