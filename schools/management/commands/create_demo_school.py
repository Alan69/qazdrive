from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from schools.models import School, DrivingCategory
from userconf.models import UserRole, UserSchoolRole

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a demo driving school and link all superusers to it'

    def handle(self, *args, **options):
        # Get or create driving categories first
        categories = []
        for code in ['A', 'B', 'C']:
            cat, created = DrivingCategory.objects.get_or_create(
                code=code,
                defaults={
                    'name': f'Категория {code}',
                    'description': f'Водительская категория {code}'
                }
            )
            categories.append(cat)
            if created:
                self.stdout.write(f'Created category: {code}')
        
        # Create demo school
        from datetime import date, timedelta
        
        school, created = School.objects.get_or_create(
            bin_iin='123456789012',
            defaults={
                'name': 'Демо Автошкола',
                'short_name': 'Демо АШ',
                'address': 'г. Алматы, ул. Демонстрационная, 1',
                'director_iin': '990101300123',
                'director_full_name': 'Иванов Иван Иванович',
                'phone': '+77001234567',
                'email': 'demo@avtomektep.kz',
                'license_number': 'DEMO-2024-001',
                'license_issue_date': date.today(),
                'license_expiry_date': date.today() + timedelta(days=365*5),
                'is_active': True,
                'cashback_certificate_percent': 5.0,
                'cashback_aitest_percent': 10.0,
                'allow_electronic_certificates': True,
            }
        )
        
        if created:
            # Add categories to school
            school.categories.set(categories)
            self.stdout.write(self.style.SUCCESS(f'Created demo school: {school.name}'))
        else:
            self.stdout.write(f'School already exists: {school.name}')
        
        # Get platform admin role
        platform_admin_role, _ = UserRole.objects.get_or_create(
            code='platform_admin',
            defaults={
                'name': 'Администратор платформы',
                'description': 'Полный доступ ко всем функциям платформы'
            }
        )
        
        # Link all superusers to this school
        superusers = User.objects.filter(is_superuser=True)
        
        for user in superusers:
            # Set platform admin flag
            if not user.is_platform_admin:
                user.is_platform_admin = True
                user.save()
            
            # Create school role
            school_role, role_created = UserSchoolRole.objects.get_or_create(
                user=user,
                school=school,
                defaults={'role': platform_admin_role}
            )
            
            if role_created:
                self.stdout.write(f'  Linked superuser {user.phone_number} to demo school')
            else:
                self.stdout.write(f'  Superuser {user.phone_number} already linked')
        
        if superusers.exists():
            self.stdout.write(self.style.SUCCESS(
                f'Successfully linked {superusers.count()} superuser(s) to demo school'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                'No superusers found. Create a superuser first with: python manage.py createsuperuser'
            ))

