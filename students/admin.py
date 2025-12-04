from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import StudentGroup, Student, StudentDocument, LessonRecord, ExamResult


class StudentInline(admin.TabularInline):
    model = Student
    extra = 0
    fields = ('full_name', 'iin', 'phone', 'status', 'enrollment_date')
    readonly_fields = ('full_name',)
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'ФИО'


@admin.register(StudentGroup)
class StudentGroupAdmin(ImportExportModelAdmin):
    list_display = ('name', 'school', 'category', 'status', 'students_count', 'start_date', 'end_date')
    list_filter = ('status', 'category', 'school', 'start_date')
    search_fields = ('name', 'school__name')
    readonly_fields = ('created_at', 'updated_at', 'students_count')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('school', 'name', 'category', 'max_students')
        }),
        ('Персонал', {
            'fields': ('teacher', 'driving_instructor', 'production_master')
        }),
        ('Расположение', {
            'fields': ('cabinet',)
        }),
        ('Расписание', {
            'fields': ('start_date', 'end_date')
        }),
        ('Статус', {
            'fields': ('status', 'notes')
        }),
        ('Статистика', {
            'fields': ('students_count',),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [StudentInline]
    
    def students_count(self, obj):
        return obj.students_count
    students_count.short_description = 'Курсантов'


class StudentDocumentInline(admin.TabularInline):
    model = StudentDocument
    extra = 0
    fields = ('document_type', 'title', 'file', 'created_at')
    readonly_fields = ('created_at',)


class LessonRecordInline(admin.TabularInline):
    model = LessonRecord
    extra = 0
    fields = ('lesson_type', 'date', 'status', 'duration_minutes')


class ExamResultInline(admin.TabularInline):
    model = ExamResult
    extra = 0
    fields = ('exam_type', 'exam_date', 'result', 'score')


@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    list_display = ('full_name', 'iin', 'group', 'phone', 'status', 'registry_verified', 'enrollment_date')
    list_filter = ('status', 'registry_verified', 'group__school', 'group', 'enrollment_date')
    search_fields = ('last_name', 'first_name', 'middle_name', 'iin', 'phone', 'group__name')
    readonly_fields = ('created_at', 'updated_at', 'full_name', 'school')
    
    fieldsets = (
        ('Личные данные', {
            'fields': ('last_name', 'first_name', 'middle_name', 'iin', 'birth_date', 'photo')
        }),
        ('Контакты', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Обучение', {
            'fields': ('group', 'user', 'enrollment_date', 'contract_number')
        }),
        ('Медицинская справка', {
            'fields': ('medical_certificate_number', 'medical_certificate_date', 'medical_certificate_valid_until')
        }),
        ('Статус', {
            'fields': ('status', 'registry_verified', 'registry_verification_date', 'notes')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [StudentDocumentInline, LessonRecordInline, ExamResultInline]


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ('student', 'document_type', 'title', 'uploaded_by', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('student__last_name', 'student__first_name', 'title')
    readonly_fields = ('created_at',)


@admin.register(LessonRecord)
class LessonRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson_type', 'date', 'status', 'duration_minutes', 'instructor')
    list_filter = ('lesson_type', 'status', 'date')
    search_fields = ('student__last_name', 'student__first_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam_type', 'exam_date', 'result', 'score', 'errors_count')
    list_filter = ('exam_type', 'result', 'exam_date')
    search_fields = ('student__last_name', 'student__first_name')
    readonly_fields = ('created_at',)
    date_hierarchy = 'exam_date'
