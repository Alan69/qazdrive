from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator


# BIN/IIN Validator for Kazakhstan Business/Individual Identification Number
bin_iin_validator = RegexValidator(
    regex=r'^\d{12}$',
    message='БИН/ИИН должен содержать ровно 12 цифр'
)


class DrivingCategory(models.Model):
    """Driving license categories (A, B, BE, C, CE, D, DE, Tm, Tb)"""
    code = models.CharField(max_length=10, unique=True, verbose_name="Код категории")
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    class Meta:
        verbose_name = 'Категория прав'
        verbose_name_plural = 'Категории прав'
        ordering = ['code']
    
    def __str__(self):
        return self.code


class School(models.Model):
    """Driving school (auto-school) main model"""
    
    # Basic info
    bin_iin = models.CharField(
        max_length=12,
        validators=[bin_iin_validator],
        unique=True,
        db_index=True,
        verbose_name="БИН/ИИН"
    )
    name = models.CharField(max_length=255, verbose_name="Название")
    short_name = models.CharField(max_length=100, blank=True, verbose_name="Краткое название")
    
    # Director info
    director_iin = models.CharField(
        max_length=12,
        validators=[bin_iin_validator],
        verbose_name="ИИН директора"
    )
    director_full_name = models.CharField(max_length=255, verbose_name="Ф.И.О. директора")
    
    # Contact info
    address = models.CharField(max_length=500, verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Основной телефон")
    email = models.EmailField(blank=True, verbose_name="Email")
    
    # License info
    license_number = models.CharField(max_length=100, verbose_name="Номер кв. св. директора")
    license_issue_date = models.DateField(verbose_name="Дата выпуска кв. св. директора")
    license_expiry_date = models.DateField(verbose_name="Дата истечения кв. св.")
    
    # Categories this school can teach
    categories = models.ManyToManyField(DrivingCategory, related_name='schools', verbose_name="Категории для обучения")
    
    # Financial settings
    cashback_certificate_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="Кешбек за сертификат (%)"
    )
    cashback_aitest_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="Кешбек за AITest (%)"
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Баланс")
    
    # Electronic certificates
    allow_electronic_certificates = models.BooleanField(
        default=True,
        verbose_name="Возможность получать электронные свидетельства через Avtomektep"
    )
    
    # Logo/branding
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True, verbose_name="Логотип")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    is_verified = models.BooleanField(default=False, verbose_name="Верифицирована")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = 'Автошкола'
        verbose_name_plural = 'Автошколы'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def total_groups(self):
        return self.groups.count()
    
    @property
    def active_groups(self):
        return self.groups.filter(status__in=['enrolling', 'training']).count()
    
    @property
    def total_students(self):
        from students.models import Student
        return Student.objects.filter(group__school=self).count()


class SchoolCabinet(models.Model):
    """School classroom/office locations"""
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='cabinets', verbose_name="Автошкола")
    address = models.CharField(max_length=500, verbose_name="Адрес")
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending',
        verbose_name="Статус согласования"
    )
    rejection_reason = models.TextField(blank=True, verbose_name="Причина отклонения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата одобрения")
    
    class Meta:
        verbose_name = 'Кабинет'
        verbose_name_plural = 'Кабинеты'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.school.name} - {self.address}"


class Vehicle(models.Model):
    """Training vehicles for driving practice"""
    
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('maintenance', 'На обслуживании'),
        ('inactive', 'Неактивный'),
    ]
    
    TRANSMISSION_CHOICES = [
        ('manual', 'МКПП'),
        ('automatic', 'АКПП'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='vehicles', verbose_name="Автошкола")
    brand = models.CharField(max_length=100, verbose_name="Марка")
    model = models.CharField(max_length=100, verbose_name="Модель")
    plate_number = models.CharField(max_length=20, verbose_name="Гос. номер")
    category = models.ForeignKey(DrivingCategory, on_delete=models.SET_NULL, null=True, verbose_name="Категория")
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='manual', verbose_name="КПП")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    description = models.TextField(blank=True, verbose_name="Описание")
    year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Год выпуска")
    
    # Photo
    photo = models.ImageField(upload_to='vehicle_photos/', null=True, blank=True, verbose_name="Фото")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Транспортное средство'
        verbose_name_plural = 'Транспортные средства'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate_number})"
    
    @property
    def full_name(self):
        return f"{self.brand} {self.model}"


class CatalogCard(models.Model):
    """School catalog cards for public listing"""
    
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('archived', 'В архиве'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='catalog_cards', verbose_name="Автошкола")
    name = models.CharField(max_length=255, verbose_name="Название")
    category = models.ForeignKey(DrivingCategory, on_delete=models.SET_NULL, null=True, verbose_name="Категория")
    description = models.TextField(blank=True, verbose_name="Описание")
    address = models.CharField(max_length=500, blank=True, verbose_name="Адрес филиала")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    price_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена от")
    price_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена до")
    
    # Images
    image = models.ImageField(upload_to='catalog_images/', null=True, blank=True, verbose_name="Изображение")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    is_active = models.BooleanField(default=True, verbose_name="Отображать в каталоге")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Карточка в каталоге'
        verbose_name_plural = 'Карточки в каталоге'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.school.name})"


class SchoolTransaction(models.Model):
    """Financial transactions for schools"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('cashback_certificate', 'Кешбек за сертификат'),
        ('cashback_aitest', 'Кешбек за AITest'),
        ('deposit', 'Пополнение'),
        ('withdrawal', 'Вывод средств'),
        ('fee', 'Комиссия'),
        ('refund', 'Возврат'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='transactions', verbose_name="Автошкола")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPE_CHOICES, verbose_name="Тип")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # For balance history tracking
    balance_before = models.DecimalField(max_digits=12, decimal_places=2, null=True, verbose_name="Баланс до")
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, null=True, verbose_name="Баланс после")
    
    # Related user (who initiated)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='school_transactions',
        verbose_name="Пользователь"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = 'Транзакция школы'
        verbose_name_plural = 'Транзакции школ'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.school.name} - {self.get_transaction_type_display()} - {self.amount}₸"


class SchoolContract(models.Model):
    """Contracts/agreements for schools"""
    
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('active', 'Активный'),
        ('expired', 'Истёк'),
        ('terminated', 'Расторгнут'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='contracts', verbose_name="Автошкола")
    contract_number = models.CharField(max_length=100, unique=True, verbose_name="Номер договора")
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата окончания")
    
    document = models.FileField(upload_to='contracts/', null=True, blank=True, verbose_name="Документ")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    is_active = models.BooleanField(default=False, verbose_name="Модуль договоров активен")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Договор'
        verbose_name_plural = 'Договоры'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.contract_number} - {self.school.name}"
