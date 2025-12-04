from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Complete setup for Avtomektep platform (run this after migrations)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('AVTOMEKTEP PLATFORM SETUP'))
        self.stdout.write(self.style.WARNING('=' * 60))
        
        # Step 1: Setup initial data
        self.stdout.write('\n[1/3] Setting up initial data (categories, roles, subjects)...')
        try:
            call_command('setup_initial_data')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            return
        
        # Step 2: Create demo school
        self.stdout.write('\n[2/3] Creating demo school...')
        try:
            call_command('create_demo_school')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            return
        
        # Step 3: Grant superuser access
        self.stdout.write('\n[3/3] Granting superuser access...')
        try:
            call_command('grant_superuser_access')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            return
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✓ AVTOMEKTEP PLATFORM SETUP COMPLETE!'))
        self.stdout.write('=' * 60)
        self.stdout.write('\nYou can now:')
        self.stdout.write('  1. Login at http://localhost/')
        self.stdout.write('  2. Access demo school from the sidebar')
        self.stdout.write('  3. Create students, staff, and certificates')
        self.stdout.write('')

