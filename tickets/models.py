from django.db import models
from django.conf import settings


class TicketSubject(models.Model):
    """Predefined ticket subjects/categories"""
    
    name = models.CharField(max_length=255, verbose_name="Тема")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    
    class Meta:
        verbose_name = 'Тема обращения'
        verbose_name_plural = 'Темы обращений'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Ticket(models.Model):
    """Support tickets (Заявки/Обращения)"""
    
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('waiting', 'Ожидает ответа'),
        ('resolved', 'Решён'),
        ('closed', 'Закрыт'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('urgent', 'Срочный'),
    ]
    
    # Who created the ticket
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name="Пользователь"
    )
    
    # School related (if ticket is about a specific school)
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name="Автошкола"
    )
    
    # Ticket details
    subject = models.ForeignKey(
        TicketSubject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Тема"
    )
    custom_subject = models.CharField(max_length=255, blank=True, verbose_name="Тема (свободный ввод)")
    description = models.TextField(verbose_name="Описание проблемы")
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="Приоритет")
    
    # Assignment
    assigned_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name="Администратор"
    )
    
    # Resolution
    resolution = models.TextField(blank=True, verbose_name="Решение")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата решения")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']
    
    def get_subject_display(self):
        if self.subject:
            return self.subject.name
        return self.custom_subject or "Без темы"
    
    def __str__(self):
        return f"#{self.id} - {self.get_subject_display()} ({self.user})"


class TicketMessage(models.Model):
    """Messages within a ticket (conversation thread)"""
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Заявка"
    )
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ticket_messages',
        verbose_name="Отправитель"
    )
    
    message = models.TextField(verbose_name="Сообщение")
    
    # Attachments
    attachment = models.FileField(
        upload_to='ticket_attachments/',
        null=True,
        blank=True,
        verbose_name="Вложение"
    )
    
    # Is this a system message (auto-generated)?
    is_system_message = models.BooleanField(default=False, verbose_name="Системное сообщение")
    
    # Is this message from admin/support?
    is_admin_response = models.BooleanField(default=False, verbose_name="Ответ администратора")
    
    # Read status
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата прочтения")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")
    
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender} on ticket #{self.ticket.id}"


class TicketNotification(models.Model):
    """Notifications about ticket updates"""
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Заявка"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ticket_notifications',
        verbose_name="Пользователь"
    )
    
    message = models.CharField(max_length=500, verbose_name="Уведомление")
    
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата прочтения")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = 'Уведомление о заявке'
        verbose_name_plural = 'Уведомления о заявках'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user} - ticket #{self.ticket.id}"
