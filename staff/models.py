from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator


# IIN Validator
iin_validator = RegexValidator(
    regex=r'^\d{12}$',
    message='ИИН должен содержать ровно 12 цифр'
)


class BaseStaffMember(models.Model):
    """Abstract base class for all staff members"""
    
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('inactive', 'Неактивный'),
        ('archived', 'В архиве'),
    ]
    
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        verbose_name="Автошкола"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь системы"
    )
    
    iin = models.CharField(
        max_length=12,
        validators=[iin_validator],
        verbose_name="ИИН",
        db_index=True
    )
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    middle_name = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    notes = models.TextField(blank=True, verbose_name="Примечание")
    needs_info_update = models.BooleanField(default=True, verbose_name="Необходимо обновить информацию")
    
    # Photo
    photo = models.ImageField(upload_to='staff_photos/', null=True, blank=True, verbose_name="Фото")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        abstract = True
    
    @property
    def full_name(self):
        """Returns full name in format: LASTNAME FIRSTNAME MIDDLENAME"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(filter(None, parts)).upper()
    
    def __str__(self):
        return self.full_name


class Teacher(BaseStaffMember):
    """Teachers (Преподаватели) - theoretical instruction"""
    
    POSITION_CHOICES = [
        ('teacher', 'Преподаватель'),
        ('senior_teacher', 'Старший преподаватель'),
        ('head_teacher', 'Заведующий учебной частью'),
    ]
    
    position = models.CharField(
        max_length=30,
        choices=POSITION_CHOICES,
        default='teacher',
        verbose_name="Должность"
    )
    
    # Qualification
    qualification_number = models.CharField(max_length=100, blank=True, verbose_name="Номер квалификационного свидетельства")
    qualification_issue_date = models.DateField(null=True, blank=True, verbose_name="Дата выдачи кв. св.")
    qualification_expiry_date = models.DateField(null=True, blank=True, verbose_name="Дата истечения кв. св.")
    
    # Categories they can teach
    teaching_categories = models.ManyToManyField(
        'schools.DrivingCategory',
        blank=True,
        related_name='teachers',
        verbose_name="Категории преподавания"
    )
    
    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        ordering = ['-created_at']
        unique_together = ['school', 'iin']
    
    def save(self, *args, **kwargs):
        # Set related_name for foreign key
        self._meta.get_field('school').remote_field.related_name = 'teachers'
        super().save(*args, **kwargs)


class DrivingInstructor(BaseStaffMember):
    """Driving Instructors (Мастера обучения вождению)"""
    
    POSITION_CHOICES = [
        ('instructor', 'Водитель'),
        ('senior_instructor', 'Старший инструктор'),
    ]
    
    position = models.CharField(
        max_length=30,
        choices=POSITION_CHOICES,
        default='instructor',
        verbose_name="Должность"
    )
    
    # Driver's license info
    license_number = models.CharField(max_length=50, blank=True, verbose_name="Номер водительского удостоверения")
    license_issue_date = models.DateField(null=True, blank=True, verbose_name="Дата выдачи ВУ")
    license_expiry_date = models.DateField(null=True, blank=True, verbose_name="Дата истечения ВУ")
    
    # Categories they can teach
    license_categories = models.ManyToManyField(
        'schools.DrivingCategory',
        blank=True,
        related_name='driving_instructors',
        verbose_name="Категории ВУ"
    )
    
    # Assigned vehicle
    assigned_vehicle = models.ForeignKey(
        'schools.Vehicle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instructors',
        verbose_name="Закреплённое ТС"
    )
    
    class Meta:
        verbose_name = 'Мастер обучения вождению'
        verbose_name_plural = 'Мастера обучения вождению'
        ordering = ['-created_at']
        unique_together = ['school', 'iin']
    
    def save(self, *args, **kwargs):
        self._meta.get_field('school').remote_field.related_name = 'driving_instructors'
        super().save(*args, **kwargs)


class ProductionMaster(BaseStaffMember):
    """Production Training Masters (Мастера производственного обучения)"""
    
    POSITION_CHOICES = [
        ('master', 'Мастер'),
        ('senior_master', 'Старший мастер'),
    ]
    
    position = models.CharField(
        max_length=30,
        choices=POSITION_CHOICES,
        default='master',
        verbose_name="Должность"
    )
    
    # Qualification
    qualification_number = models.CharField(max_length=100, blank=True, verbose_name="Номер квалификационного свидетельства")
    qualification_issue_date = models.DateField(null=True, blank=True, verbose_name="Дата выдачи кв. св.")
    qualification_expiry_date = models.DateField(null=True, blank=True, verbose_name="Дата истечения кв. св.")
    
    # Categories
    teaching_categories = models.ManyToManyField(
        'schools.DrivingCategory',
        blank=True,
        related_name='production_masters',
        verbose_name="Категории обучения"
    )
    
    class Meta:
        verbose_name = 'Мастер производственного обучения'
        verbose_name_plural = 'Мастера производственного обучения'
        ordering = ['-created_at']
        unique_together = ['school', 'iin']
    
    def save(self, *args, **kwargs):
        self._meta.get_field('school').remote_field.related_name = 'production_masters'
        super().save(*args, **kwargs)


class Employee(models.Model):
    """General school employees (administrators, secretaries, etc.)"""
    
    POSITION_CHOICES = [
        ('director', 'Директор'),
        ('deputy_director', 'Заместитель директора'),
        ('administrator', 'Администратор'),
        ('secretary', 'Секретарь'),
        ('accountant', 'Бухгалтер'),
        ('manager', 'Менеджер'),
        ('other', 'Другое'),
    ]
    
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name="Автошкола"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employments',
        verbose_name="Пользователь системы"
    )
    
    iin = models.CharField(
        max_length=12,
        validators=[iin_validator],
        verbose_name="ИИН",
        blank=True,
        db_index=True
    )
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    middle_name = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    
    position = models.CharField(
        max_length=30,
        choices=POSITION_CHOICES,
        default='other',
        verbose_name="Должность"
    )
    custom_position = models.CharField(max_length=100, blank=True, verbose_name="Другая должность")
    
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['-created_at']
        unique_together = ['school', 'email']
    
    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(filter(None, parts)).upper()
    
    def get_position_display_custom(self):
        if self.position == 'other' and self.custom_position:
            return self.custom_position
        return self.get_position_display()
    
    def __str__(self):
        return f"{self.full_name} - {self.get_position_display_custom()}"
