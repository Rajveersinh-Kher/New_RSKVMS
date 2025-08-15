from django.contrib.sessions.models import Session
from django.utils import timezone
from django.conf import settings
import os
import hashlib

class SessionInvalidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Check if this is a server restart by looking for a restart flag
        self._check_server_restart()

    def _check_server_restart(self):
        """Check if server has restarted and invalidate all sessions if so"""
        restart_flag_file = 'server_restart_flag.txt'
        
        # Create a unique server identifier based on settings
        server_id = hashlib.md5(str(settings.SECRET_KEY).encode()).hexdigest()[:8]
        
        # If restart flag doesn't exist or has different server ID, clear sessions
        should_clear = False
        if not os.path.exists(restart_flag_file):
            should_clear = True
        else:
            try:
                with open(restart_flag_file, 'r') as f:
                    stored_server_id = f.read().strip()
                if stored_server_id != server_id:
                    should_clear = True
            except:
                should_clear = True
        
        if should_clear and getattr(settings, 'CLEAR_SESSIONS_ON_RESTART', True):
            # Clear all existing sessions
            session_count = Session.objects.count()
            Session.objects.all().delete()
            
            # Create restart flag file with server ID
            with open(restart_flag_file, 'w') as f:
                f.write(server_id)
            
            print(f"Server restart detected. Cleared {session_count} user sessions.")

    def __call__(self, request):
        response = self.get_response(request)
        return response 