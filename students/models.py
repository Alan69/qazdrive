from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils import timezone


# IIN Validator
iin_validator = RegexValidator(
    regex=r'^\d{12}$',
    message='ИИН должен содержать ровно 12 цифр'
)


class StudentGroup(models.Model):
    """Study groups (Учебные группы)"""
    
    STATUS_CHOICES = [
        ('enrolling', 'Идет набор'),
        ('training', 'Идет обучение'),
        ('exams', 'Экзамены'),
        ('completed', 'Завершенные'),
        ('frozen', 'Заморожена'),
        ('cancelled', 'Отменена'),
    ]
    
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name="Автошкола"
    )
    
    name = models.CharField(max_length=100, verbose_name="Название группы")
    category = models.ForeignKey(
        'schools.DrivingCategory',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория"
    )
    
    # Staff assignments
    teacher = models.ForeignKey(
        'staff.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='groups',
        verbose_name="Преподаватель"
    )
    driving_instructor = models.ForeignKey(
        'staff.DrivingInstructor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='groups',
        verbose_name="Мастер обучения вождению"
    )
    production_master = models.ForeignKey(
        'staff.ProductionMaster',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='groups',
        verbose_name="Мастер производственного обучения"
    )
    
    # Cabinet
    cabinet = models.ForeignKey(
        'schools.SchoolCabinet',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='groups',
        verbose_name="Кабинет"
    )
    
    # Schedule
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата окончания")
    
    # Capacity
    max_students = models.PositiveIntegerField(default=30, verbose_name="Максимум курсантов")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolling', verbose_name="Статус")
    
    # Notes
    notes = models.TextField(blank=True, verbose_name="Примечания")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Учебная группа'
        verbose_name_plural = 'Учебные группы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.school.name})"
    
    @property
    def students_count(self):
        return self.students.count()
    
    @property
    def available_slots(self):
        return self.max_students - self.students_count
    
    @property
    def is_full(self):
        return self.students_count >= self.max_students


class Student(models.Model):
    """Students/Cadets (Курсанты)"""
    
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('completed', 'Завершил обучение'),
        ('expelled', 'Отчислен'),
        ('transferred', 'Переведён'),
        ('frozen', 'Заморожен'),
    ]
    
    group = models.ForeignKey(
        StudentGroup,
        on_delete=models.CASCADE,
        related_name='students',
        verbose_name="Учебная группа"
    )
    
    # Link to platform user (optional - student might not have account)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_profiles',
        verbose_name="Пользователь платформы"
    )
    
    # Personal info
    iin = models.CharField(
        max_length=12,
        validators=[iin_validator],
        verbose_name="ИИН",
        db_index=True
    )
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    middle_name = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    
    # Contact
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.CharField(max_length=500, blank=True, verbose_name="Адрес")
    
    # Photo
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True, verbose_name="Фото")
    
    # Enrollment info
    enrollment_date = models.DateField(default=timezone.now, verbose_name="Дата зачисления")
    contract_number = models.CharField(max_length=100, blank=True, verbose_name="Номер договора")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    
    # Registry verification (external verification with government systems)
    registry_verified = models.BooleanField(default=False, verbose_name="Проверен в реестре")
    registry_verification_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата верификации")
    
    # Medical certificate
    medical_certificate_number = models.CharField(max_length=100, blank=True, verbose_name="Номер мед. справки")
    medical_certificate_date = models.DateField(null=True, blank=True, verbose_name="Дата мед. справки")
    medical_certificate_valid_until = models.DateField(null=True, blank=True, verbose_name="Срок действия мед. справки")
    
    # Notes
    notes = models.TextField(blank=True, verbose_name="Примечания")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Курсант'
        verbose_name_plural = 'Курсанты'
        ordering = ['-created_at']
        # A student can only be in one group at a time with the same IIN
        unique_together = ['group', 'iin']
    
    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(filter(None, parts))
    
    @property
    def school(self):
        return self.group.school
    
    def __str__(self):
        return f"{self.full_name} ({self.iin})"


class StudentDocument(models.Model):
    """Documents uploaded for students"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('passport', 'Удостоверение личности'),
        ('medical', 'Медицинская справка'),
        ('photo', 'Фотография 3x4'),
        ('contract', 'Договор'),
        ('payment', 'Квитанция об оплате'),
        ('certificate', 'Свидетельство'),
        ('other', 'Другое'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name="Курсант"
    )
    
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name="Тип документа"
    )
    title = models.CharField(max_length=255, verbose_name="Название")
    file = models.FileField(upload_to='student_documents/', verbose_name="Файл")
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Загружено пользователем"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    
    class Meta:
        verbose_name = 'Документ курсанта'
        verbose_name_plural = 'Документы курсантов'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.get_document_type_display()}"


class LessonRecord(models.Model):
    """Records of lessons/classes attended"""
    
    LESSON_TYPE_CHOICES = [
        ('theory', 'Теория'),
        ('driving', 'Вождение'),
        ('production', 'Производственное обучение'),
        ('exam_internal', 'Внутренний экзамен'),
        ('exam_external', 'Экзамен в ГАИ'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Запланировано'),
        ('completed', 'Проведено'),
        ('missed', 'Пропущено'),
        ('cancelled', 'Отменено'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Курсант"
    )
    
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, verbose_name="Тип занятия")
    date = models.DateField(verbose_name="Дата")
    start_time = models.TimeField(null=True, blank=True, verbose_name="Время начала")
    end_time = models.TimeField(null=True, blank=True, verbose_name="Время окончания")
    
    # Duration in minutes
    duration_minutes = models.PositiveIntegerField(default=45, verbose_name="Продолжительность (мин)")
    
    # Instructor (can be teacher, driving instructor, or production master)
    instructor_teacher = models.ForeignKey(
        'staff.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lessons',
        verbose_name="Преподаватель"
    )
    instructor_driving = models.ForeignKey(
        'staff.DrivingInstructor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lessons',
        verbose_name="Мастер вождения"
    )
    instructor_production = models.ForeignKey(
        'staff.ProductionMaster',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lessons',
        verbose_name="Мастер произв. обучения"
    )
    
    # Vehicle used (for driving lessons)
    vehicle = models.ForeignKey(
        'schools.Vehicle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lessons',
        verbose_name="Транспортное средство"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Статус")
    
    # Notes and feedback
    notes = models.TextField(blank=True, verbose_name="Заметки")
    grade = models.PositiveIntegerField(null=True, blank=True, verbose_name="Оценка")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Запись о занятии'
        verbose_name_plural = 'Записи о занятиях'
        ordering = ['-date', '-start_time']
    
    @property
    def instructor(self):
        """Returns the instructor based on lesson type"""
        if self.lesson_type == 'theory':
            return self.instructor_teacher
        elif self.lesson_type == 'driving':
            return self.instructor_driving
        elif self.lesson_type == 'production':
            return self.instructor_production
        return None
    
    def __str__(self):
        return f"{self.student.full_name} - {self.get_lesson_type_display()} - {self.date}"


class ExamResult(models.Model):
    """Exam results for students"""
    
    EXAM_TYPE_CHOICES = [
        ('theory_internal', 'Теория (внутренний)'),
        ('practice_internal', 'Практика (внутренний)'),
        ('theory_gai', 'Теория (ГАИ)'),
        ('practice_gai', 'Практика (ГАИ)'),
    ]
    
    RESULT_CHOICES = [
        ('passed', 'Сдал'),
        ('failed', 'Не сдал'),
        ('absent', 'Не явился'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='exam_results',
        verbose_name="Курсант"
    )
    
    exam_type = models.CharField(max_length=30, choices=EXAM_TYPE_CHOICES, verbose_name="Тип экзамена")
    exam_date = models.DateField(verbose_name="Дата экзамена")
    
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, verbose_name="Результат")
    score = models.PositiveIntegerField(null=True, blank=True, verbose_name="Баллы")
    errors_count = models.PositiveIntegerField(default=0, verbose_name="Количество ошибок")
    
    notes = models.TextField(blank=True, verbose_name="Примечания")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Результат экзамена'
        verbose_name_plural = 'Результаты экзаменов'
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.get_exam_type_display()} - {self.get_result_display()}"
