from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from visitorapi.models import VisitRequest
from django.conf import settings
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Send notification email if visitor did not check out by end time.'

    def handle(self, *args, **options):
        now = timezone.localtime()
        today = now.date()
        overdue_visits = []
        for visit in VisitRequest.objects.filter(overdue_notification_sent=False):
            # Determine current day number for multi-day visits
            day_num = visit.get_current_day_number()
            if not (1 <= day_num <= 10):
                continue
            checkin_field = f'day_{day_num}_checkin'
            checkout_field = f'day_{day_num}_checkout'
            checkin_time = getattr(visit, checkin_field)
            checkout_time = getattr(visit, checkout_field)
            # Only consider if checked in but not checked out
            if checkin_time and not checkout_time:
                # Compose today's end datetime (combine visit_date + end_time for today)
                end_dt = datetime.combine(today, visit.end_time)
                end_dt = timezone.make_aware(end_dt, timezone.get_current_timezone())
                if now > end_dt:
                    overdue_visits.append(visit)
        for visit in overdue_visits:
            # Gather recipient emails
            recipients = set()
            if visit.host and visit.host.email:
                recipients.add(visit.host.email)
            if visit.created_by and visit.created_by.email:
                recipients.add(visit.created_by.email)
            if visit.visitor and visit.visitor.email:
                recipients.add(visit.visitor.email)
            if not recipients:
                continue
            subject = f"Visitor Overdue Checkout Alert: {visit.visitor}"
            message = (
                f"Visitor {visit.visitor} (Company: {visit.visitor.company})\n"
                f"Visit Date: {visit.visit_date}\n"
                f"Purpose: {visit.purpose}\n"
                f"Expected End Time: {visit.end_time.strftime('%H:%M:%S')}\n"
                f"Checked in at: {checkin_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"\nThis visitor has not checked out as of {now.strftime('%Y-%m-%d %H:%M:%S')} (IST).\n"
                f"Please take necessary action."
            )
            # For company: configure EMAIL_HOST, EMAIL_PORT, etc. in settings.py
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, list(recipients), fail_silently=False)
            print(f"Sent overdue checkout email for VisitRequest {visit.id} to: {', '.join(recipients)}")
            visit.overdue_notification_sent = True
            visit.save(update_fields=['overdue_notification_sent']) 