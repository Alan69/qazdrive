from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
# Create your models here.

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, first_name, last_name, city, **extra_fields):
        if not email:
            raise ValueError("Необходимо указать адрес электронной почты")
        if not password:
            raise ValueError("Необходимо ввести пароль")
        
        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            city = city,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password, first_name, last_name, city, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, first_name, last_name, city, password, **extra_fields)
    
    def create_superuser(self, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, first_name, last_name, **extra_fields)

CITIES = (
    ('Astana', 'Астана'),
    ('Almaty', 'Алматы'),
     )

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(db_index=True, unique=True, max_length=254, verbose_name="Email")
    first_name = models.CharField(max_length=250, verbose_name="Имя")
    last_name = models.CharField(max_length=250, verbose_name="Фамилия")
    city = models.CharField(max_length=250, choices=CITIES, verbose_name="Выберите город")
    forget_password_token = models.CharField(max_length=100)
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = "Users"