from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import transaction
from visitorapi.models import Visitor, VisitRequest, VisitorCard
from visitorapi.mongo_models import MongoVisitor, MongoVisitRequest, MongoVisitorCard
import os
import shutil

class Command(BaseCommand):
    help = 'Clear all visitor data from both SQLite and MongoDB while preserving HR users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force clear all data without confirmation',
        )
        parser.add_argument(
            '--sqlite-only',
            action='store_true',
            help='Clear only SQLite data (keep MongoDB data)',
        )
        parser.add_argument(
            '--mongodb-only',
            action='store_true',
            help='Clear only MongoDB data (keep SQLite data)',
        )
        parser.add_argument(
            '--media-files',
            action='store_true',
            help='Also delete media files (photos, QR codes)',
        )

    def handle(self, *args, **options):
        if not options['force']:
            self.stdout.write(self.style.WARNING('⚠️  WARNING: This will delete ALL visitor data!'))
            self.stdout.write('This operation will:')
            self.stdout.write('  - Delete all visitors from SQLite')
            self.stdout.write('  - Delete all visit requests from SQLite')
            self.stdout.write('  - Delete all visitor cards from SQLite')
            self.stdout.write('  - Delete all visitors from MongoDB')
            self.stdout.write('  - Delete all visit requests from MongoDB')
            self.stdout.write('  - Delete all visitor cards from MongoDB')
            
            if options['media_files']:
                self.stdout.write('  - Delete all visitor photos and QR codes')
            
            self.stdout.write('  - PRESERVE HR users and authentication data')
            
            confirm = input('\nAre you absolutely sure you want to proceed? Type "YES" to confirm: ')
            if confirm != 'YES':
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        # Get the user model
        User = get_user_model()
        
        # Count existing data
        sqlite_visitors = Visitor.objects.count()
        sqlite_requests = VisitRequest.objects.count()
        sqlite_cards = VisitorCard.objects.count()
        
        mongo_visitors = MongoVisitor.objects.count()
        mongo_requests = MongoVisitRequest.objects.count()
        mongo_cards = MongoVisitorCard.objects.count()
        
        self.stdout.write(f'\n📊 Current data counts:')
        self.stdout.write(f'  SQLite: {sqlite_visitors} visitors, {sqlite_requests} requests, {sqlite_cards} cards')
        self.stdout.write(f'  MongoDB: {mongo_visitors} visitors, {mongo_requests} requests, {mongo_cards} cards')

        # Clear SQLite data
        if not options['mongodb_only']:
            self.stdout.write('\n🗄️  Clearing SQLite data...')
            try:
                with transaction.atomic():
                    # Delete in correct order to avoid foreign key constraints
                    deleted_cards = VisitorCard.objects.all().delete()
                    deleted_requests = VisitRequest.objects.all().delete()
                    deleted_visitors = Visitor.objects.all().delete()
                    
                    self.stdout.write(f'  ✅ Deleted {deleted_cards[0]} visitor cards')
                    self.stdout.write(f'  ✅ Deleted {deleted_requests[0]} visit requests')
                    self.stdout.write(f'  ✅ Deleted {deleted_visitors[0]} visitors')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error clearing SQLite data: {e}'))

        # Clear MongoDB data
        if not options['sqlite_only']:
            self.stdout.write('\n🍃 Clearing MongoDB data...')
            try:
                # Clear MongoDB collections
                deleted_mongo_cards = MongoVisitorCard.objects.all().delete()
                deleted_mongo_requests = MongoVisitRequest.objects.all().delete()
                deleted_mongo_visitors = MongoVisitor.objects.all().delete()
                
                # MongoDB delete() returns the count directly, not a tuple like SQLite
                self.stdout.write(f'  ✅ Deleted {deleted_mongo_cards} visitor cards')
                self.stdout.write(f'  ✅ Deleted {deleted_mongo_requests} visit requests')
                self.stdout.write(f'  ✅ Deleted {deleted_mongo_visitors} visitors')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error clearing MongoDB data: {e}'))

        # Clear media files if requested
        if options['media_files']:
            self.stdout.write('\n📁 Clearing media files...')
            try:
                media_root = settings.MEDIA_ROOT
                
                # Clear visitor photos
                photos_dir = os.path.join(media_root, 'visitor_photos')
                if os.path.exists(photos_dir):
                    photo_count = len([f for f in os.listdir(photos_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.gif', '.avif'))])
                    shutil.rmtree(photos_dir)
                    os.makedirs(photos_dir, exist_ok=True)
                    self.stdout.write(f'  ✅ Deleted {photo_count} visitor photos')
                
                # Clear QR codes
                qr_dir = os.path.join(media_root, 'visitor_qrcodes')
                if os.path.exists(qr_dir):
                    qr_count = len([f for f in os.listdir(qr_dir) if f.endswith('.png')])
                    shutil.rmtree(qr_dir)
                    os.makedirs(qr_dir, exist_ok=True)
                    self.stdout.write(f'  ✅ Deleted {qr_count} QR code images')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error clearing media files: {e}'))

        # Summary
        self.stdout.write('\n🎯 Operation Summary:')
        if not options['mongodb_only']:
            self.stdout.write(f'  SQLite: Cleared {sqlite_visitors + sqlite_requests + sqlite_cards} records')
        if not options['sqlite_only']:
            self.stdout.write(f'  MongoDB: Cleared {mongo_visitors + mongo_requests + mongo_cards} records')
        if options['media_files']:
            self.stdout.write('  Media: Cleared all visitor photos and QR codes')
        
        self.stdout.write('\n✅ Data clearing completed successfully!')
        self.stdout.write('📝 Note: HR users and authentication data have been preserved.')
        self.stdout.write('🔄 You may need to restart your Django application.')
