from mongoengine import Document, StringField, EmailField, ImageField, DateTimeField, BooleanField, DateField, IntField, ReferenceField, EmbeddedDocumentField, EmbeddedDocument, ListField
import qrcode
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django.utils import timezone

class MongoVisitor(Document):
    """MongoDB model for Visitor - keeping same field names for Excel compatibility"""
    first_name = StringField(required=True, max_length=100)
    last_name = StringField(required=True, max_length=100)
    email = EmailField(unique=True, null=True, blank=True)
    phone = StringField(required=True, max_length=20)
    company = StringField(required=True, max_length=200)
    id_proof_type = StringField(required=True, max_length=50)
    id_proof_number = StringField(required=True, max_length=100)
    photo = StringField(null=True, blank=True)  # Store file path/URL
    created_at = DateTimeField(default=lambda: timezone.localtime(timezone.now()))
    updated_at = DateTimeField(default=lambda: timezone.localtime(timezone.now()))
    
    meta = {
        'collection': 'visitors',
        'indexes': [
            'email',
            ('first_name', 'last_name', 'phone', 'company'),  # Compound index for unique constraint
        ]
    }
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.company})"

class MongoVisitRequest(Document):
    """MongoDB model for VisitRequest - keeping same field names for Excel compatibility"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Reference to visitor (store visitor ID as string for now)
    visitor_id = StringField(required=True)
    host_id = StringField(required=True)  # Reference to HRUser ID
    purpose = StringField(required=True)
    other_purpose = StringField(max_length=255, blank=True, null=True)
    visit_date = DateField(required=True)
    start_time = DateTimeField(null=True, blank=True)
    end_time = StringField(required=True)  # Store as string for compatibility
    status = StringField(choices=STATUS_CHOICES, default='PENDING', max_length=20)
    allow_mobile = BooleanField(default=False)
    allow_laptop = BooleanField(default=False)
    approved_by_id = StringField(null=True, blank=True)  # Reference to HRUser ID
    created_at = DateTimeField(default=lambda: timezone.localtime(timezone.now()))
    updated_at = DateTimeField(default=lambda: timezone.localtime(timezone.now()))
    requestedByEmployee = BooleanField(default=False)
    reference_employee_name = StringField(max_length=100, blank=True, null=True)
    reference_employee_department = StringField(max_length=100, blank=True, null=True)
    reference_purpose = StringField(max_length=255, blank=True, null=True)
    created_by_id = StringField(null=True, blank=True)  # Reference to HRUser ID
    checkin_time = DateTimeField(null=True, blank=True)
    checkout_time = DateTimeField(null=True, blank=True)
    checkout_by_hr = BooleanField(default=False)
    valid_upto = DateField(null=True, blank=True)
    
    # Multi-day check-in/check-out fields (10 days maximum)
    day_1_checkin = DateTimeField(null=True, blank=True)
    day_1_checkout = DateTimeField(null=True, blank=True)
    day_2_checkin = DateTimeField(null=True, blank=True)
    day_2_checkout = DateTimeField(null=True, blank=True)
    day_3_checkin = DateTimeField(null=True, blank=True)
    day_3_checkout = DateTimeField(null=True, blank=True)
    day_4_checkin = DateTimeField(null=True, blank=True)
    day_4_checkout = DateTimeField(null=True, blank=True)
    day_5_checkin = DateTimeField(null=True, blank=True)
    day_5_checkout = DateTimeField(null=True, blank=True)
    day_6_checkin = DateTimeField(null=True, blank=True)
    day_6_checkout = DateTimeField(null=True, blank=True)
    day_7_checkin = DateTimeField(null=True, blank=True)
    day_7_checkout = DateTimeField(null=True, blank=True)
    day_8_checkin = DateTimeField(null=True, blank=True)
    day_8_checkout = DateTimeField(null=True, blank=True)
    day_9_checkin = DateTimeField(null=True, blank=True)
    day_9_checkout = DateTimeField(null=True, blank=True)
    day_10_checkin = DateTimeField(null=True, blank=True)
    day_10_checkout = DateTimeField(null=True, blank=True)
    overdue_notification_sent = BooleanField(default=False)
    
    meta = {
        'collection': 'visit_requests',
        'indexes': [
            'visitor_id',
            'host_id',
            'status',
            'visit_date',
            'created_at'
        ]
    }
    
    def __str__(self):
        return f"Visit request for visitor {self.visitor_id} on {self.visit_date}"
    
    def can_check_in_today(self):
        """Check if visitor can check in today"""
        from datetime import date
        today = date.today()
        
        # Check if today is within the valid period
        if self.valid_upto and today > self.valid_upto:
            return False
        
        # Check if today is the visit date or within the valid period
        if self.visit_date and today < self.visit_date:
            return False
        
        return True
    
    def can_check_out_today(self):
        """Check if visitor can check out today (must be checked in first)"""
        from datetime import date
        today = date.today()
        
        # Check if today is within the valid period
        if self.valid_upto and today > self.valid_upto:
            return False
        
        # Check if today is the visit date or within the valid period
        if self.visit_date and today < self.visit_date:
            return False
        
        # Check if already checked in today
        checkin_field = self.get_today_checkin_field()
        if not checkin_field:
            return False
        
        checkin_time = getattr(self, checkin_field)
        if not checkin_time:
            return False
        
        # Check if already checked out today
        checkout_field = self.get_today_checkout_field()
        if checkout_field:
            checkout_time = getattr(self, checkout_field)
            if checkout_time:
                return False
        
        return True
    
    def get_today_checkin_field(self):
        """Get the check-in field name for today"""
        from datetime import date
        today = date.today()
        
        if not self.visit_date:
            return None
        
        # Calculate days difference
        days_diff = (today - self.visit_date).days
        
        # Only allow check-in for the first 10 days
        if days_diff < 0 or days_diff >= 10:
            return None
        
        return f'day_{days_diff + 1}_checkin'
    
    def get_today_checkout_field(self):
        """Get the check-out field name for today"""
        from datetime import date
        today = date.today()
        
        if not self.visit_date:
            return None
        
        # Calculate days difference
        days_diff = (today - self.visit_date).days
        
        # Only allow check-out for the first 10 days
        if days_diff < 0 or days_diff >= 10:
            return None
        
        return f'day_{days_diff + 1}_checkout'

class MongoVisitorCard(Document):
    """MongoDB model for VisitorCard - keeping same field names for Excel compatibility"""
    CARD_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('RETURNED', 'Returned'),
        ('LOST', 'Lost'),
    ]
    
    visit_request_id = StringField(required=True)  # Reference to VisitRequest ID
    card_number = StringField(required=True, max_length=50, unique=True)
    issued_at = DateTimeField(default=lambda: timezone.localtime(timezone.now()))
    returned_at = DateTimeField(null=True, blank=True)
    status = StringField(choices=CARD_STATUS_CHOICES, default='ACTIVE', max_length=20)
    issued_by_id = StringField(null=True, blank=True)  # Reference to HRUser ID
    qr_code_image = StringField(null=True, blank=True)  # Store file path/URL
    printed = BooleanField(default=False)
    
    meta = {
        'collection': 'visitor_cards',
        'indexes': [
            'card_number',
            'visit_request_id',
            'status',
            'issued_at'
        ]
    }
    
    def __str__(self):
        return f"Card {self.card_number} for visit request {self.visit_request_id}"
    
    def save(self, *args, **kwargs):
        print(f"SAVE CALLED for card_number={self.card_number}")
        super().save(*args, **kwargs)
        if not self.qr_code_image:
            print(f"Generating QR for card_number={self.card_number}")
            self.generate_and_save_qr_code()
    
    def generate_and_save_qr_code(self):
        print(f"GENERATE QR CALLED for card_number={self.card_number}")
        import os
        from django.conf import settings
        
        # Create QR code data
        qr_data = f"{self.card_number}|{self.visit_request_id}|{timezone.localtime(timezone.now()).date()}"
        print(f"QR data generated: {qr_data}")
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Ensure the directory exists
        qr_dir = os.path.join(settings.MEDIA_ROOT, 'visitor_qrcodes')
        os.makedirs(qr_dir, exist_ok=True)
        
        # Save QR code image
        qr_filename = f"qr_{self.card_number}.png"
        qr_path = os.path.join(qr_dir, qr_filename)
        qr_image.save(qr_path)
        
        # Update the model with the file path
        self.qr_code_image = qr_filename
        super().save(update_fields=['qr_code_image'])
    
    @property
    def qr_code_url(self):
        if self.qr_code_image:
            return f"/media/visitor_qrcodes/{self.qr_code_image}"
        return ""
