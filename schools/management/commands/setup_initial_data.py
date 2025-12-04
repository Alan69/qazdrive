from django.core.management.base import BaseCommand
from schools.models import DrivingCategory
from userconf.models import UserRole
from tickets.models import TicketSubject


class Command(BaseCommand):
    help = 'Set up initial data for Avtomektep platform'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create driving categories
        self.create_categories()
        
        # Create user roles
        self.create_roles()
        
        # Create ticket subjects
        self.create_ticket_subjects()
        
        self.stdout.write(self.style.SUCCESS('Initial data setup complete!'))

    def create_categories(self):
        """Create Kazakhstan driving license categories"""
        categories = [
            ('A', 'Мотоциклы', 'Мотоциклы и мототранспортные средства'),
            ('B', 'Легковые автомобили', 'Автомобили до 3500 кг'),
            ('BE', 'Легковые с прицепом', 'Автомобили категории B с прицепом'),
            ('C', 'Грузовые автомобили', 'Автомобили свыше 3500 кг'),
            ('CE', 'Грузовые с прицепом', 'Автомобили категории C с прицепом'),
            ('D', 'Автобусы', 'Автобусы для перевозки пассажиров'),
            ('DE', 'Автобусы с прицепом', 'Автобусы категории D с прицепом'),
            ('Tm', 'Трамвай', 'Трамвай'),
            ('Tb', 'Троллейбус', 'Троллейбус'),
        ]
        
        for code, name, description in categories:
            cat, created = DrivingCategory.objects.get_or_create(
                code=code,
                defaults={'name': name, 'description': description}
            )
            if created:
                self.stdout.write(f'  Created category: {code}')
            else:
                self.stdout.write(f'  Category exists: {code}')

    def create_roles(self):
        """Create user roles"""
        roles = [
            ('platform_admin', 'Администратор платформы', 'Полный доступ ко всем функциям платформы'),
            ('school_director', 'Директор автошколы', 'Управление автошколой, полный доступ к данным школы'),
            ('school_manager', 'Менеджер автошколы', 'Управление группами, курсантами и персоналом'),
            ('teacher', 'Преподаватель', 'Доступ к группам и теоретическим занятиям'),
            ('driving_instructor', 'Мастер обучения вождению', 'Доступ к практическим занятиям по вождению'),
            ('production_master', 'Мастер производственного обучения', 'Доступ к производственным занятиям'),
            ('employee', 'Сотрудник', 'Базовый доступ к системе'),
            ('student', 'Курсант', 'Доступ к личному кабинету курсанта'),
        ]
        
        for code, name, description in roles:
            role, created = UserRole.objects.get_or_create(
                code=code,
                defaults={'name': name, 'description': description}
            )
            if created:
                self.stdout.write(f'  Created role: {name}')
            else:
                self.stdout.write(f'  Role exists: {name}')

    def create_ticket_subjects(self):
        """Create predefined ticket subjects"""
        subjects = [
            ('Проблемы с обучением', 'Вопросы связанные с учебным процессом', 1),
            ('Замарозка', 'Заморозка обучения', 2),
            ('Технические проблемы', 'Проблемы с работой системы', 3),
            ('Оплата и финансы', 'Вопросы по оплате и транзакциям', 4),
            ('Сертификаты', 'Вопросы по электронным свидетельствам', 5),
            ('Изменение данных', 'Запрос на изменение персональных данных', 6),
            ('Другое', 'Другие вопросы', 99),
        ]
        
        for name, description, order in subjects:
            subject, created = TicketSubject.objects.get_or_create(
                name=name,
                defaults={'description': description, 'order': order}
            )
            if created:
                self.stdout.write(f'  Created subject: {name}')
            else:
                self.stdout.write(f'  Subject exists: {name}')

