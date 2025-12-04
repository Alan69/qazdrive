from django.contrib import admin
from .models import TicketSubject, Ticket, TicketMessage, TicketNotification


@admin.register(TicketSubject)
class TicketSubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('order', 'name')


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    fields = ('sender', 'message', 'is_admin_response', 'is_read', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_subject_display', 'user', 'school', 'status', 'priority', 'assigned_admin', 'created_at')
    list_filter = ('status', 'priority', 'subject', 'school', 'created_at')
    search_fields = ('user__phone_number', 'user__first_name', 'user__last_name', 'custom_subject', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Заявка', {
            'fields': ('user', 'school', 'subject', 'custom_subject', 'description')
        }),
        ('Статус', {
            'fields': ('status', 'priority', 'assigned_admin')
        }),
        ('Решение', {
            'fields': ('resolution', 'resolved_at')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [TicketMessageInline]


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'sender', 'is_admin_response', 'is_read', 'created_at')
    list_filter = ('is_admin_response', 'is_read', 'is_system_message', 'created_at')
    search_fields = ('ticket__id', 'sender__phone_number', 'message')
    readonly_fields = ('created_at',)


@admin.register(TicketNotification)
class TicketNotificationAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('ticket__id', 'user__phone_number', 'message')
    readonly_fields = ('created_at',)
