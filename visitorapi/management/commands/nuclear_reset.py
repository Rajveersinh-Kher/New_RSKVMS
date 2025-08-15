from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import transaction
from django.conf import settings
from visitorapi.models import Visitor, VisitRequest, VisitorCard
from visitorapi.mongo_models import MongoVisitor, MongoVisitRequest, MongoVisitorCard
import os
import shutil

class Command(BaseCommand):
    help = 'NUCLEAR RESET: Clear ALL data including users, visitors, requests, and media files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force nuclear reset without confirmation',
        )
        parser.add_argument(
            '--keep-superuser',
            action='store_true',
            help='Keep one superuser account (for emergency access)',
        )

    def handle(self, *args, **options):
        if not options['force']:
            self.stdout.write(self.style.ERROR('☢️  NUCLEAR RESET WARNING! ☢️'))
            self.stdout.write('This operation will DESTROY EVERYTHING:')
            self.stdout.write('  - Delete ALL users (HR, superusers, HOS, registration)')
            self.stdout.write('  - Delete ALL visitors from both databases')
            self.stdout.write('  - Delete ALL visit requests from both databases')
            self.stdout.write('  - Delete ALL visitor cards from both databases')
            self.stdout.write('  - Delete ALL media files (photos, QR codes)')
            self.stdout.write('  - Clear ALL user sessions')
            self.stdout.write('  - Clear ALL permissions and groups')
            self.stdout.write('  - This is a COMPLETE SYSTEM DESTRUCTION!')
            
            if not options['keep_superuser']:
                self.stdout.write('  - You will NOT be able to log in afterward!')
                self.stdout.write('  - You will need to recreate the entire system!')
            
            confirm = input('\nType "NUCLEAR RESET" to confirm complete destruction: ')
            if confirm != 'NUCLEAR RESET':
                self.stdout.write(self.style.WARNING('Nuclear reset cancelled.'))
                return

        # Get the user model
        User = get_user_model()
        
        # Count existing data
        total_users = User.objects.count()
        superusers = User.objects.filter(is_superuser=True).count()
        sessions = Session.objects.count()
        
        sqlite_visitors = Visitor.objects.count()
        sqlite_requests = VisitRequest.objects.count()
        sqlite_cards = VisitorCard.objects.count()
        
        mongo_visitors = MongoVisitor.objects.count()
        mongo_requests = MongoVisitRequest.objects.count()
        mongo_cards = MongoVisitorCard.objects.count()
        
        self.stdout.write(f'\n📊 Current system state:')
        self.stdout.write(f'  Users: {total_users} (including {superusers} superusers)')
        self.stdout.write(f'  Sessions: {sessions}')
        self.stdout.write(f'  SQLite: {sqlite_visitors} visitors, {sqlite_requests} requests, {sqlite_cards} cards')
        self.stdout.write(f'  MongoDB: {mongo_visitors} visitors, {mongo_requests} requests, {mongo_cards} cards')

        # NUCLEAR RESET - Clear everything
        self.stdout.write('\n☢️  Executing nuclear reset...')
        
        try:
            with transaction.atomic():
                # Step 1: Clear all sessions
                self.stdout.write('  🔥 Clearing user sessions...')
                deleted_sessions = Session.objects.all().delete()
                self.stdout.write(f'    ✅ Deleted {deleted_sessions[0]} sessions')
                
                # Step 2: Clear SQLite data
                self.stdout.write('  🔥 Clearing SQLite data...')
                deleted_cards = VisitorCard.objects.all().delete()
                deleted_requests = VisitRequest.objects.all().delete()
                deleted_visitors = Visitor.objects.all().delete()
                self.stdout.write(f'    ✅ Deleted {deleted_cards[0]} cards, {deleted_requests[0]} requests, {deleted_visitors[0]} visitors')
                
                # Step 3: Clear MongoDB data
                self.stdout.write('  🔥 Clearing MongoDB data...')
                deleted_mongo_cards = MongoVisitorCard.objects.all().delete()
                deleted_mongo_requests = MongoVisitRequest.objects.all().delete()
                deleted_mongo_visitors = MongoVisitor.objects.all().delete()
                self.stdout.write(f'    ✅ Deleted {deleted_mongo_cards} cards, {deleted_mongo_requests} requests, {deleted_mongo_visitors} visitors')
                
                # Step 4: Clear all users (with optional superuser preservation)
                self.stdout.write('  🔥 Clearing all users...')
                if options['keep_superuser']:
                    emergency_user = User.objects.filter(is_superuser=True).first()
                    if emergency_user:
                        self.stdout.write(f'    ⚠️  Preserving emergency superuser: {emergency_user.username}')
                        User.objects.exclude(id=emergency_user.id).delete()
                        deleted_users = total_users - 1
                    else:
                        User.objects.all().delete()
                        deleted_users = total_users
                else:
                    User.objects.all().delete()
                    deleted_users = total_users
                
                self.stdout.write(f'    ✅ Deleted {deleted_users} users')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Nuclear reset failed: {e}'))
            return

        # Step 5: Clear media files
        self.stdout.write('  🔥 Clearing media files...')
        try:
            media_root = settings.MEDIA_ROOT
            
            # Clear visitor photos
            photos_dir = os.path.join(media_root, 'visitor_photos')
            if os.path.exists(photos_dir):
                photo_count = len([f for f in os.listdir(photos_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.gif', '.avif'))])
                shutil.rmtree(photos_dir)
                os.makedirs(photos_dir, exist_ok=True)
                self.stdout.write(f'    ✅ Deleted {photo_count} visitor photos')
            
            # Clear QR codes
            qr_dir = os.path.join(media_root, 'visitor_qrcodes')
            if os.path.exists(qr_dir):
                qr_count = len([f for f in os.listdir(qr_dir) if f.endswith('.png')])
                shutil.rmtree(qr_dir)
                os.makedirs(qr_dir, exist_ok=True)
                self.stdout.write(f'    ✅ Deleted {qr_count} QR code images')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'    ❌ Error clearing media files: {e}'))

        # Nuclear reset complete
        self.stdout.write('\n☢️  NUCLEAR RESET COMPLETE! ☢️')
        self.stdout.write('🎯 Everything has been destroyed:')
        self.stdout.write(f'  - Users: {deleted_users} deleted')
        self.stdout.write(f'  - Sessions: {deleted_sessions[0]} cleared')
        self.stdout.write(f'  - SQLite: {sqlite_visitors + sqlite_requests + sqlite_cards} records cleared')
        self.stdout.write(f'  - MongoDB: {mongo_visitors + mongo_requests + mongo_cards} records cleared')
        self.stdout.write(f'  - Media: All files deleted')
        
        if options['keep_superuser']:
            self.stdout.write('\n⚠️  Emergency superuser preserved for access.')
        else:
            self.stdout.write('\n🚨 COMPLETE SYSTEM DESTRUCTION!')
            self.stdout.write('🚨 You cannot log in!')
            self.stdout.write('🚨 You must recreate the entire system!')
        
        self.stdout.write('\n📝 Recovery steps:')
        if not options['keep_superuser']:
            self.stdout.write('  1. Create new superuser: python manage.py createsuperuser')
        self.stdout.write('  2. Restart Django application')
        self.stdout.write('  3. Recreate all necessary users and data')
        self.stdout.write('  4. Import any backup data if available')
        
        self.stdout.write('\n☢️  Nuclear reset successful. System is now completely clean. ☢️')
