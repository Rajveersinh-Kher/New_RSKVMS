from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.contrib.sessions.models import Session
import os
import shutil

class Command(BaseCommand):
    help = 'Clear ALL users (HR, superusers, HOS) and reset the system completely'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force clear all users without confirmation',
        )
        parser.add_argument(
            '--keep-superuser',
            action='store_true',
            help='Keep one superuser account (for emergency access)',
        )
        parser.add_argument(
            '--media-files',
            action='store_true',
            help='Also delete all media files (photos, QR codes)',
        )

    def handle(self, *args, **options):
        if not options['force']:
            self.stdout.write(self.style.ERROR('⚠️  CRITICAL WARNING: This will delete ALL users!'))
            self.stdout.write('This operation will:')
            self.stdout.write('  - Delete ALL HR users')
            self.stdout.write('  - Delete ALL superusers')
            self.stdout.write('  - Delete ALL HOS users')
            self.stdout.write('  - Delete ALL registration users')
            self.stdout.write('  - Clear ALL user sessions')
            self.stdout.write('  - Clear ALL user permissions and groups')
            
            if options['media_files']:
                self.stdout.write('  - Delete ALL media files')
            
            self.stdout.write('  - You will NOT be able to log in afterward!')
            self.stdout.write('  - This is a COMPLETE system reset!')
            
            confirm = input('\nAre you absolutely sure you want to proceed? Type "DELETE ALL USERS" to confirm: ')
            if confirm != 'DELETE ALL USERS':
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        # Get the user model
        User = get_user_model()
        
        # Count existing data
        total_users = User.objects.count()
        superusers = User.objects.filter(is_superuser=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        active_users = User.objects.filter(is_active=True).count()
        sessions = Session.objects.count()
        
        self.stdout.write(f'\n📊 Current user counts:')
        self.stdout.write(f'  Total Users: {total_users}')
        self.stdout.write(f'  Superusers: {superusers}')
        self.stdout.write(f'  Staff Users: {staff_users}')
        self.stdout.write(f'  Active Users: {active_users}')
        self.stdout.write(f'  Active Sessions: {sessions}')

        # Clear all users
        self.stdout.write('\n🗑️  Clearing all users...')
        try:
            with transaction.atomic():
                # Clear all sessions first
                deleted_sessions = Session.objects.all().delete()
                self.stdout.write(f'  ✅ Deleted {deleted_sessions[0]} user sessions')
                
                # Clear all users
                if options['keep_superuser']:
                    # Keep one superuser for emergency access
                    emergency_user = User.objects.filter(is_superuser=True).first()
                    if emergency_user:
                        self.stdout.write(f'  ⚠️  Keeping emergency superuser: {emergency_user.username}')
                        User.objects.exclude(id=emergency_user.id).delete()
                        deleted_count = total_users - 1
                    else:
                        User.objects.all().delete()
                        deleted_count = total_users
                else:
                    # Delete ALL users
                    deleted_count = User.objects.all().delete()[0]
                
                self.stdout.write(f'  ✅ Deleted {deleted_count} users')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error clearing users: {e}'))
            return

        # Clear media files if requested
        if options['media_files']:
            self.stdout.write('\n📁 Clearing media files...')
            try:
                from django.conf import settings
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
        self.stdout.write(f'  Users: Deleted {deleted_count} users')
        self.stdout.write(f'  Sessions: Deleted {sessions} sessions')
        if options['media_files']:
            self.stdout.write('  Media: Cleared all files')
        
        self.stdout.write('\n✅ User clearing completed successfully!')
        
        if options['keep_superuser']:
            self.stdout.write('⚠️  Emergency superuser account preserved for access.')
        else:
            self.stdout.write('🚨 ALL users have been deleted!')
            self.stdout.write('🚨 You will NOT be able to log in!')
            self.stdout.write('🚨 You need to create a new superuser account!')
        
        self.stdout.write('\n📝 Next steps:')
        if not options['keep_superuser']:
            self.stdout.write('  1. Create a new superuser: python manage.py createsuperuser')
        self.stdout.write('  2. Restart your Django application')
        self.stdout.write('  3. Log in with the new account')
