from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from userconf.models import UserRole, UserSchoolRole
from schools.models import School

User = get_user_model()


class Command(BaseCommand):
    help = 'Grant all superusers platform admin access and link them to all schools'

    def handle(self, *args, **options):
        # Get or create platform_admin role
        platform_admin_role, created = UserRole.objects.get_or_create(
            code='platform_admin',
            defaults={
                'name': 'Администратор платформы',
                'description': 'Полный доступ ко всем функциям платформы'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created platform_admin role'))
        
        # Get all superusers
        superusers = User.objects.filter(is_superuser=True)
        
        if not superusers.exists():
            self.stdout.write(self.style.WARNING('No superusers found'))
            return
        
        for user in superusers:
            # Set is_platform_admin flag
            if not user.is_platform_admin:
                user.is_platform_admin = True
                user.save()
                self.stdout.write(f'Set is_platform_admin=True for user: {user.phone_number}')
            
            # Link user to all existing schools with platform_admin role
            schools = School.objects.all()
            
            if schools.exists():
                for school in schools:
                    school_role, created = UserSchoolRole.objects.get_or_create(
                        user=user,
                        school=school,
                        defaults={'role': platform_admin_role}
                    )
                    if created:
                        self.stdout.write(f'  Linked {user.phone_number} to school: {school.name}')
                    else:
                        self.stdout.write(f'  Already linked to school: {school.name}')
            else:
                self.stdout.write(self.style.WARNING(
                    f'No schools found. User {user.phone_number} is platform admin but not linked to any schools yet.'
                ))
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully granted platform admin access to {superusers.count()} superuser(s)'
        ))

