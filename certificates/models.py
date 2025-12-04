from django.db import models
from django.conf import settings
import uuid
from io import BytesIO
from django.core.files import File

# QR code generation is optional - only used when issuing certificates
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


def generate_certificate_number():
    """Generate unique certificate number"""
    import random
    import string
    from datetime import datetime
    
    year = datetime.now().year
    random_part = ''.join(random.choices(string.digits, k=8))
    return f"CERT-{year}-{random_part}"


class Certificate(models.Model):
    """Electronic certificates for completed students"""
    
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('issued', 'Выдан'),
        ('revoked', 'Отозван'),
        ('expired', 'Истёк'),
    ]
    
    # Unique identifier for verification
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    
    # Certificate number
    certificate_number = models.CharField(
        max_length=50,
        unique=True,
        default=generate_certificate_number,
        verbose_name="Номер свидетельства"
    )
    
    # Student link
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name="Курсант"
    )
    
    # School link
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name="Автошкола"
    )
    
    # Category
    category = models.ForeignKey(
        'schools.DrivingCategory',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория"
    )
    
    # Certificate details
    issue_date = models.DateField(verbose_name="Дата выдачи")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Дата истечения")
    
    # Training period
    training_start_date = models.DateField(null=True, blank=True, verbose_name="Начало обучения")
    training_end_date = models.DateField(null=True, blank=True, verbose_name="Окончание обучения")
    
    # Hours completed
    theory_hours = models.PositiveIntegerField(default=0, verbose_name="Часов теории")
    practice_hours = models.PositiveIntegerField(default=0, verbose_name="Часов практики")
    
    # Exam results
    theory_exam_passed = models.BooleanField(default=False, verbose_name="Теория сдана")
    practice_exam_passed = models.BooleanField(default=False, verbose_name="Практика сдана")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    
    # QR Code for verification
    qr_code = models.ImageField(upload_to='certificate_qr/', null=True, blank=True, verbose_name="QR код")
    
    # PDF file
    pdf_file = models.FileField(upload_to='certificate_pdfs/', null=True, blank=True, verbose_name="PDF файл")
    
    # Who issued
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issued_certificates',
        verbose_name="Кем выдан"
    )
    
    # Notes
    notes = models.TextField(blank=True, verbose_name="Примечания")
    
    # If revoked
    revocation_reason = models.TextField(blank=True, verbose_name="Причина отзыва")
    revoked_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата отзыва")
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revoked_certificates',
        verbose_name="Кем отозван"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Электронное свидетельство'
        verbose_name_plural = 'Электронные свидетельства'
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.certificate_number} - {self.student.full_name}"
    
    @property
    def is_valid(self):
        """Check if certificate is currently valid"""
        from django.utils import timezone
        if self.status != 'issued':
            return False
        if self.expiry_date and self.expiry_date < timezone.now().date():
            return False
        return True
    
    @property
    def verification_url(self):
        """Generate verification URL"""
        return f"/verify/certificate/{self.uuid}/"
    
    def generate_qr_code(self, base_url="https://avtomektep.kz"):
        """Generate QR code for certificate verification"""
        if not HAS_QRCODE:
            return  # Skip if qrcode library not installed
        
        verification_url = f"{base_url}/verify/certificate/{self.uuid}/"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'qr_{self.certificate_number}.png'
        
        self.qr_code.save(filename, File(buffer), save=False)
        buffer.close()
    
    def save(self, *args, **kwargs):
        # Generate certificate number if not set
        if not self.certificate_number:
            self.certificate_number = generate_certificate_number()
        
        super().save(*args, **kwargs)
        
        # Generate QR code if status is issued and no QR yet
        if self.status == 'issued' and not self.qr_code:
            self.generate_qr_code()
            super().save(update_fields=['qr_code'])


class CertificateVerification(models.Model):
    """Log of certificate verification attempts"""
    
    certificate = models.ForeignKey(
        Certificate,
        on_delete=models.CASCADE,
        related_name='verifications',
        verbose_name="Свидетельство"
    )
    
    # Who verified (if authenticated)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Проверил"
    )
    
    # Verification details
    verified_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата проверки")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP адрес")
    user_agent = models.TextField(null=True, blank=True, verbose_name="User Agent")
    
    # Result
    is_valid = models.BooleanField(verbose_name="Действителен")
    verification_message = models.CharField(max_length=500, blank=True, verbose_name="Результат проверки")
    
    class Meta:
        verbose_name = 'Проверка свидетельства'
        verbose_name_plural = 'Проверки свидетельств'
        ordering = ['-verified_at']
    
    def __str__(self):
        status = "Действителен" if self.is_valid else "Недействителен"
        return f"{self.certificate.certificate_number} - {status} - {self.verified_at}"


class CertificateTemplate(models.Model):
    """Templates for generating certificate PDFs"""
    
    name = models.CharField(max_length=255, verbose_name="Название шаблона")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # Template file (HTML or PDF template)
    template_file = models.FileField(
        upload_to='certificate_templates/',
        verbose_name="Файл шаблона"
    )
    
    # Category specific
    category = models.ForeignKey(
        'schools.DrivingCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Для категории"
    )
    
    # School specific (if null, available for all schools)
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='certificate_templates',
        verbose_name="Для автошколы"
    )
    
    is_default = models.BooleanField(default=False, verbose_name="Шаблон по умолчанию")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Шаблон свидетельства'
        verbose_name_plural = 'Шаблоны свидетельств'
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return self.name
