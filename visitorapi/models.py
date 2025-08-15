from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
import os
import qrcode
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class HRUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('HR', 'HR'),
        ('REGISTRATION', 'Registration'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='HR')
    department = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})"

class Visitor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=200)
    id_proof_type = models.CharField(max_length=50)  # e.g., "Passport", "Driver's License"
    id_proof_number = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='visitor_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Add unique constraint to prevent duplicate visitors
        # This will prevent multiple visitors with same name, phone, and company
        unique_together = ['first_name', 'last_name', 'phone', 'company']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.company})"

class VisitRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    host = models.ForeignKey(HRUser, on_delete=models.CASCADE, related_name='hosted_visits')
    purpose = models.TextField()
    other_purpose = models.CharField(max_length=255, blank=True, null=True)
    visit_date = models.DateField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    allow_mobile = models.BooleanField(default=False)
    allow_laptop = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        HRUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_visits'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    requestedByEmployee = models.BooleanField(default=False)
    reference_employee_name = models.CharField(max_length=100, blank=True, null=True)
    reference_employee_department = models.CharField(max_length=100, blank=True, null=True)
    reference_purpose = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(HRUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_visits')
    checkin_time = models.DateTimeField(null=True, blank=True)  # New field for check-in
    checkout_time = models.DateTimeField(null=True, blank=True)  # New field for check-out
    checkout_by_hr = models.BooleanField(default=False)  # True if HR performed manual checkout
    valid_upto = models.DateField(null=True, blank=True)  # New field for request validity

    # Multi-day check-in/check-out fields (10 days maximum)
    day_1_checkin = models.DateTimeField(null=True, blank=True)
    day_1_checkout = models.DateTimeField(null=True, blank=True)
    day_2_checkin = models.DateTimeField(null=True, blank=True)
    day_2_checkout = models.DateTimeField(null=True, blank=True)
    day_3_checkin = models.DateTimeField(null=True, blank=True)
    day_3_checkout = models.DateTimeField(null=True, blank=True)
    day_4_checkin = models.DateTimeField(null=True, blank=True)
    day_4_checkout = models.DateTimeField(null=True, blank=True)
    day_5_checkin = models.DateTimeField(null=True, blank=True)
    day_5_checkout = models.DateTimeField(null=True, blank=True)
    day_6_checkin = models.DateTimeField(null=True, blank=True)
    day_6_checkout = models.DateTimeField(null=True, blank=True)
    day_7_checkin = models.DateTimeField(null=True, blank=True)
    day_7_checkout = models.DateTimeField(null=True, blank=True)
    day_8_checkin = models.DateTimeField(null=True, blank=True)
    day_8_checkout = models.DateTimeField(null=True, blank=True)
    day_9_checkin = models.DateTimeField(null=True, blank=True)
    day_9_checkout = models.DateTimeField(null=True, blank=True)
    day_10_checkin = models.DateTimeField(null=True, blank=True)
    day_10_checkout = models.DateTimeField(null=True, blank=True)
    overdue_notification_sent = models.BooleanField(default=False)  # New field to track overdue notification

    def __str__(self):
        return f"Visit by {self.visitor} to {self.host} on {self.visit_date}"

    def get_current_day_number(self):
        """Get the current day number based on visit_date and valid_upto"""
        if not self.valid_upto:
            return 1
        
        from datetime import date
        today = date.today()
        visit_start = self.visit_date
        
        if today < visit_start:
            return 0  # Before visit period
        
        if today > self.valid_upto:
            return -1  # After visit period
        
        # Calculate day number (1-based)
        day_diff = (today - visit_start).days
        return day_diff + 1

    def can_check_in_today(self):
        """Check if visitor can check in today"""
        current_day = self.get_current_day_number()
        return 1 <= current_day <= 10

    def can_check_out_today(self):
        """Check if visitor can check out today (must be checked in first)"""
        current_day = self.get_current_day_number()
        if not (1 <= current_day <= 10):
            return False
        
        # Check if already checked in today
        checkin_field = f'day_{current_day}_checkin'
        checkout_field = f'day_{current_day}_checkout'
        
        return (getattr(self, checkin_field) is not None and 
                getattr(self, checkout_field) is None)

    def get_today_checkin_field(self):
        """Get the checkin field name for today"""
        current_day = self.get_current_day_number()
        if 1 <= current_day <= 10:
            return f'day_{current_day}_checkin'
        return None

    def get_today_checkout_field(self):
        """Get the checkout field name for today"""
        current_day = self.get_current_day_number()
        if 1 <= current_day <= 10:
            return f'day_{current_day}_checkout'
        return None

    def migrate_old_checkin_data(self):
        """Migrate old checkin/checkout data to day_1 fields"""
        if self.checkin_time and not self.day_1_checkin:
            self.day_1_checkin = self.checkin_time
        if self.checkout_time and not self.day_1_checkout:
            self.day_1_checkout = self.checkout_time

class VisitorCard(models.Model):
    CARD_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('RETURNED', 'Returned'),
        ('LOST', 'Lost'),
    ]

    visit_request = models.OneToOneField(VisitRequest, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(default=timezone.now)
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=CARD_STATUS_CHOICES, default='ACTIVE')
    issued_by = models.ForeignKey(HRUser, on_delete=models.SET_NULL, null=True)
    qr_code_image = models.ImageField(upload_to='visitor_qrcodes/', null=True, blank=True)
    printed = models.BooleanField(default=False)

    def __str__(self):
        return f"Card {self.card_number} - {self.visit_request.visitor}"

    def save(self, *args, **kwargs):
        print(f"SAVE CALLED for card_number={self.card_number}")
        super().save(*args, **kwargs)  # Save first to get a PK
        if not self.qr_code_image:
            print(f"Generating QR for card_number={self.card_number}")
            self.generate_and_save_qr_code()

    def generate_and_save_qr_code(self):
        print(f"GENERATE QR CALLED for card_number={self.card_number}")
        qr_data = f"{self.card_number}|{self.visit_request.visitor}|{self.visit_request.visit_date}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        # Generate QR code with white background
        img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
        datas = img.getdata()
        newData = []
        for item in datas:
            # Make white pixels fully transparent
            if item[0] > 200 and item[1] > 200 and item[2] > 200:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        img.putdata(newData)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        file_name = f"qr_{self.card_number}.png"
        self.qr_code_image.save(file_name, ContentFile(buffer.getvalue()), save=False)
        super().save(update_fields=['qr_code_image'])

    @property
    def qr_code_url(self):
        if self.qr_code_image:
            return self.qr_code_image.url
        return ""
