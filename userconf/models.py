from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator


# IIN Validator for Kazakhstan Individual Identification Number (12 digits)
iin_validator = RegexValidator(
    regex=r'^\d{12}$',
    message='ИИН должен содержать ровно 12 цифр'
)


class CustomUserManager(BaseUserManager):
    def _create_user(self, phone_number, password, first_name, last_name, **extra_fields):
        if not phone_number:
            raise ValueError("Необходимо указать номер телефона")
        if not password:
            raise ValueError("Необходимо ввести пароль")
        
        user = self.model(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, phone_number, password, first_name, last_name, city=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, first_name, last_name, **extra_fields)
    
    def create_superuser(self, phone_number, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(phone_number, password, first_name, last_name, **extra_fields)

CITIES = (
    ('Astana', 'Астана'),
    ('Almaty', 'Алматы'),
    ('Aqtau', 'Актау'),
    ('Aktobe', 'Актобе'),
    ('Arqalyq', 'Аркалык'),
    ('Atbasar', 'Атбасар'),
    ('Atyrau', 'Атырау'),
    ('Zaisan', 'Зайсан'),
    ('Pavlodar', 'Павлодар'),
    ('Petropavl', 'Петропавл'),
    ('Ust-Kamenagorsk', 'Усть-Каменогорск'),
    ('Balhash', 'Балхаш'),
    ('Borovoe', 'Боровое'),
    ('Karaganda', 'Караганда'),
    ('Kokshetau', 'Кокшетау'),
    ('Kostanai', 'Костанай'),
    ('Kyzylorda', 'Кызылорда'),
    ('Ridder', 'Риддер'),
    ('Whymkent', 'Шымкент'),
    ('Zhambyl', 'Жамбыл'),
    ('Saryagash', 'Сарыагаш'),
    ('Semipalatinsk', 'Семипалатинск'),
    ('Ekibastuz', 'Экибастуз'),
    ('Zhezgazgan', 'Жезказган'),
    ('Oral', 'Орал'),
    ('Taldykorgan', 'Талдыкорган'),
    ('Turkestan', 'Туркестан'),
     )

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, verbose_name="Email", null=True, blank=True)
    phone_number = models.CharField(max_length=15, db_index=True, unique=True, verbose_name="Номер телефона")
    first_name = models.CharField(max_length=250, verbose_name="Имя")
    last_name = models.CharField(max_length=250, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=250, verbose_name="Отчество", null=True, blank=True)
    iin = models.CharField(
        max_length=12, 
        validators=[iin_validator], 
        verbose_name="ИИН",
        null=True, 
        blank=True,
        unique=True,
        db_index=True
    )
    city = models.CharField(max_length=250, choices=CITIES, verbose_name="Выберите город", null=True, blank=True)
    category = models.ForeignKey('quiz.Category', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категория")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Аватар")
    
    # Subscription/tariff related
    is_have_tarif = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)
    forget_password_token = models.CharField(max_length=100, null=True, blank=True)
    payment_id = models.IntegerField(verbose_name="ID оплаты каспи", null=True, blank=True, default=None)
    pddtest_pass = models.CharField(max_length=255, null=True, blank=True, default=None)
    tarif_name = models.CharField(max_length=255, null=True, blank=True)
    tarif_expire_date = models.DateField(null=True, blank=True)
    
    # Platform role (for global platform access)
    is_platform_admin = models.BooleanField(default=False, verbose_name="Администратор платформы")
    
    # Status fields
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.last_name} {self.first_name}"
        if self.phone_number:
            return self.phone_number
        return f"User {self.id}" if self.id else "New User"
    
    @property
    def full_name(self):
        """Returns full name in format: LASTNAME FIRSTNAME MIDDLENAME"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(filter(None, parts)).upper()
    
    def get_schools(self):
        """Returns all schools where user has a role"""
        return self.school_roles.all().values_list('school', flat=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Пользователи"


class UserRole(models.Model):
    """Available roles in the system"""
    ROLE_CHOICES = [
        ('platform_admin', 'Администратор платформы'),
        ('school_director', 'Директор автошколы'),
        ('school_manager', 'Менеджер автошколы'),
        ('teacher', 'Преподаватель'),
        ('driving_instructor', 'Мастер обучения вождению'),
        ('production_master', 'Мастер производственного обучения'),
        ('employee', 'Сотрудник'),
        ('student', 'Курсант'),
    ]
    
    code = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES, verbose_name="Код роли")
    name = models.CharField(max_length=100, verbose_name="Название роли")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'


class UserSchoolRole(models.Model):
    """Links users to schools with specific roles (many-to-many with extra data)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='school_roles', verbose_name="Пользователь")
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='user_roles', verbose_name="Автошкола")
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE, verbose_name="Роль")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата назначения")
    
    class Meta:
        verbose_name = 'Роль пользователя в автошколе'
        verbose_name_plural = 'Роли пользователей в автошколах'
        unique_together = ['user', 'school', 'role']
    
    def __str__(self):
        return f"{self.user} - {self.school} - {self.role}"


class AuthLog(models.Model):
    """Tracks all login attempts for audit purposes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_logs', verbose_name="Пользователь")
    login_time = models.DateTimeField(auto_now_add=True, verbose_name="Время входа")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP адрес")
    user_agent = models.TextField(null=True, blank=True, verbose_name="User Agent")
    is_successful = models.BooleanField(default=True, verbose_name="Успешный вход")
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name="Время выхода")
    
    class Meta:
        verbose_name = 'Журнал авторизаций'
        verbose_name_plural = 'Журнал авторизаций'
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user} - {self.login_time}"