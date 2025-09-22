from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser for the healthcare system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username for the superuser'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@healthcenter.com',
            help='Email for the superuser'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Password for the superuser'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists')
            )
            return
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='System',
            last_name='Administrator',
            user_type='admin'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created superuser "{username}"')
        )