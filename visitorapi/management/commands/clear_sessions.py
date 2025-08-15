from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone

class Command(BaseCommand):
    help = 'Clear all user sessions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force clear all sessions without confirmation',
        )

    def handle(self, *args, **options):
        if not options['force']:
            confirm = input('Are you sure you want to clear all user sessions? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        # Clear all sessions
        session_count = Session.objects.count()
        Session.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cleared {session_count} user sessions.')
        )
        self.stdout.write(
            self.style.SUCCESS('All users will need to log in again.')
        ) 