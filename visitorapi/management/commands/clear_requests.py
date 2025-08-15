from django.core.management.base import BaseCommand
from django.db import transaction
from visitorapi.models import VisitRequest, VisitorCard
from visitorapi.mongo_models import MongoVisitRequest, MongoVisitorCard

class Command(BaseCommand):
    help = 'Clear all visit requests while preserving visitor data and HR users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force clear all requests without confirmation',
        )
        parser.add_argument(
            '--sqlite-only',
            action='store_true',
            help='Clear only SQLite requests (keep MongoDB requests)',
        )
        parser.add_argument(
            '--mongodb-only',
            action='store_true',
            help='Clear only MongoDB requests (keep SQLite requests)',
        )

    def handle(self, *args, **options):
        if not options['force']:
            self.stdout.write(self.style.WARNING('⚠️  WARNING: This will delete ALL visit requests!'))
            self.stdout.write('This operation will:')
            self.stdout.write('  - Delete all visit requests from SQLite')
            self.stdout.write('  - Delete all visitor cards from SQLite')
            self.stdout.write('  - Delete all visit requests from MongoDB')
            self.stdout.write('  - Delete all visitor cards from MongoDB')
            self.stdout.write('  - PRESERVE visitor data and HR users')
            
            confirm = input('\nAre you sure you want to proceed? Type "YES" to confirm: ')
            if confirm != 'YES':
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        # Count existing data
        sqlite_requests = VisitRequest.objects.count()
        sqlite_cards = VisitorCard.objects.count()
        
        mongo_requests = MongoVisitRequest.objects.count()
        mongo_cards = MongoVisitorCard.objects.count()
        
        self.stdout.write(f'\n📊 Current request counts:')
        self.stdout.write(f'  SQLite: {sqlite_requests} requests, {sqlite_cards} cards')
        self.stdout.write(f'  MongoDB: {mongo_requests} requests, {mongo_cards} cards')

        # Clear SQLite requests
        if not options['mongodb_only']:
            self.stdout.write('\n🗄️  Clearing SQLite requests...')
            try:
                with transaction.atomic():
                    # Delete in correct order to avoid foreign key constraints
                    deleted_cards = VisitorCard.objects.all().delete()
                    deleted_requests = VisitRequest.objects.all().delete()
                    
                    self.stdout.write(f'  ✅ Deleted {deleted_cards[0]} visitor cards')
                    self.stdout.write(f'  ✅ Deleted {deleted_requests[0]} visit requests')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error clearing SQLite requests: {e}'))

        # Clear MongoDB requests
        if not options['sqlite_only']:
            self.stdout.write('\n🍃 Clearing MongoDB requests...')
            try:
                # Clear MongoDB collections
                deleted_mongo_cards = MongoVisitorCard.objects.all().delete()
                deleted_mongo_requests = MongoVisitRequest.objects.all().delete()
                
                # MongoDB delete() returns the count directly, not a tuple like SQLite
                self.stdout.write(f'  ✅ Deleted {deleted_mongo_cards} visitor cards')
                self.stdout.write(f'  ✅ Deleted {deleted_mongo_requests} visit requests')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error clearing MongoDB requests: {e}'))

        # Summary
        self.stdout.write('\n🎯 Operation Summary:')
        if not options['mongodb_only']:
            self.stdout.write(f'  SQLite: Cleared {sqlite_requests + sqlite_cards} records')
        if not options['sqlite_only']:
            self.stdout.write(f'  MongoDB: Cleared {mongo_requests + mongo_cards} records')
        
        self.stdout.write('\n✅ Request clearing completed successfully!')
        self.stdout.write('📝 Note: Visitor data and HR users have been preserved.')
        self.stdout.write('🔄 You may need to restart your Django application.')
