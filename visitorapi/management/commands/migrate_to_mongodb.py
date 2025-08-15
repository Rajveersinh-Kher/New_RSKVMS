from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from visitorapi.models import Visitor, VisitRequest, VisitorCard
from visitorapi.mongo_models import MongoVisitor, MongoVisitRequest, MongoVisitorCard
from datetime import datetime

class Command(BaseCommand):
    help = 'Migrate data from SQLite to MongoDB'

    def handle(self, *args, **options):
        self.stdout.write('Starting migration from SQLite to MongoDB...')
        
        # Get the user model
        User = get_user_model()
        
        # Step 1: Migrate Visitors
        self.stdout.write('Migrating Visitors...')
        visitors_migrated = 0
        for visitor in Visitor.objects.all():
            try:
                # Check if visitor already exists in MongoDB
                if MongoVisitor.objects.filter(
                    first_name=visitor.first_name,
                    last_name=visitor.last_name,
                    phone=visitor.phone,
                    company=visitor.company
                ).count() > 0:
                    self.stdout.write(f'Visitor {visitor.first_name} {visitor.last_name} already exists in MongoDB, skipping...')
                    continue
                
                mongo_visitor = MongoVisitor(
                    first_name=visitor.first_name,
                    last_name=visitor.last_name,
                    email=visitor.email,
                    phone=visitor.phone,
                    company=visitor.company,
                    id_proof_type=visitor.id_proof_type,
                    id_proof_number=visitor.id_proof_number,
                    photo=str(visitor.photo) if visitor.photo else None,
                    created_at=visitor.created_at,
                    updated_at=visitor.updated_at
                )
                mongo_visitor.save()
                visitors_migrated += 1
                self.stdout.write(f'Migrated visitor: {visitor.first_name} {visitor.last_name}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error migrating visitor {visitor.id}: {e}'))
        
        self.stdout.write(f'Visitors migrated: {visitors_migrated}')
        
        # Step 2: Migrate Visit Requests
        self.stdout.write('Migrating Visit Requests...')
        requests_migrated = 0
        for request in VisitRequest.objects.all():
            try:
                # Find corresponding MongoDB visitor
                mongo_visitor = MongoVisitor.objects.filter(
                    first_name=request.visitor.first_name,
                    last_name=request.visitor.last_name,
                    phone=request.visitor.phone,
                    company=request.visitor.company
                ).first()
                
                if not mongo_visitor:
                    self.stdout.write(self.style.WARNING(f'Visitor not found in MongoDB for request {request.id}, skipping...'))
                    continue
                
                # Check if request already exists
                if MongoVisitRequest.objects.filter(
                    visitor_id=str(mongo_visitor.id),
                    visit_date=request.visit_date,
                    created_at=request.created_at
                ).count() > 0:
                    self.stdout.write(f'Visit request for {request.visitor.first_name} on {request.visit_date} already exists, skipping...')
                    continue
                
                mongo_request = MongoVisitRequest(
                    visitor_id=str(mongo_visitor.id),
                    host_id=str(request.host.id),
                    purpose=request.purpose,
                    other_purpose=request.other_purpose,
                    visit_date=request.visit_date,
                    start_time=request.start_time,
                    end_time=str(request.end_time) if request.end_time else '',
                    status=request.status,
                    allow_mobile=request.allow_mobile,
                    allow_laptop=request.allow_laptop,
                    approved_by_id=str(request.approved_by.id) if request.approved_by else None,
                    created_at=request.created_at,
                    updated_at=request.updated_at,
                    requestedByEmployee=request.requestedByEmployee,
                    reference_employee_name=request.reference_employee_name,
                    reference_employee_department=request.reference_employee_department,
                    reference_purpose=request.reference_purpose,
                    created_by_id=str(request.created_by.id) if request.created_by else None,
                    checkin_time=request.checkin_time,
                    checkout_time=request.checkout_time,
                    checkout_by_hr=request.checkout_by_hr,
                    valid_upto=request.valid_upto,
                    day_1_checkin=request.day_1_checkin,
                    day_1_checkout=request.day_1_checkout,
                    day_2_checkin=request.day_2_checkin,
                    day_2_checkout=request.day_2_checkout,
                    day_3_checkin=request.day_3_checkin,
                    day_3_checkout=request.day_3_checkout,
                    day_4_checkin=request.day_4_checkin,
                    day_4_checkout=request.day_4_checkout,
                    day_5_checkin=request.day_5_checkin,
                    day_5_checkout=request.day_5_checkout,
                    day_6_checkin=request.day_6_checkin,
                    day_6_checkout=request.day_6_checkout,
                    day_7_checkin=request.day_7_checkin,
                    day_7_checkout=request.day_7_checkout,
                    day_8_checkin=request.day_8_checkin,
                    day_8_checkout=request.day_8_checkout,
                    day_9_checkin=request.day_9_checkin,
                    day_9_checkout=request.day_9_checkout,
                    day_10_checkin=request.day_10_checkin,
                    day_10_checkout=request.day_10_checkout,
                    overdue_notification_sent=request.overdue_notification_sent
                )
                mongo_request.save()
                requests_migrated += 1
                self.stdout.write(f'Migrated visit request: {request.id}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error migrating visit request {request.id}: {e}'))
        
        self.stdout.write(f'Visit requests migrated: {requests_migrated}')
        
        # Step 3: Migrate Visitor Cards
        self.stdout.write('Migrating Visitor Cards...')
        cards_migrated = 0
        for card in VisitorCard.objects.all():
            try:
                # Find corresponding MongoDB visit request
                mongo_request = MongoVisitRequest.objects.filter(
                    visitor_id__in=[v.id for v in MongoVisitor.objects.filter(
                        first_name=card.visit_request.visitor.first_name,
                        last_name=card.visit_request.visitor.last_name,
                        phone=card.visit_request.visitor.phone,
                        company=card.visit_request.visitor.company
                    )],
                    visit_date=card.visit_request.visit_date,
                    created_at=card.visit_request.created_at
                ).first()
                
                if not mongo_request:
                    self.stdout.write(self.style.WARNING(f'Visit request not found in MongoDB for card {card.id}, skipping...'))
                    continue
                
                # Check if card already exists
                if MongoVisitorCard.objects.filter(card_number=card.card_number).count() > 0:
                    self.stdout.write(f'Card {card.card_number} already exists, skipping...')
                    continue
                
                mongo_card = MongoVisitorCard(
                    visit_request_id=str(mongo_request.id),
                    card_number=card.card_number,
                    issued_at=card.issued_at,
                    returned_at=card.returned_at,
                    status=card.status,
                    issued_by_id=str(card.issued_by.id) if card.issued_by else None,
                    qr_code_image=str(card.qr_code_image) if card.qr_code_image else None,
                    printed=card.printed
                )
                mongo_card.save()
                cards_migrated += 1
                self.stdout.write(f'Migrated visitor card: {card.card_number}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error migrating visitor card {card.id}: {e}'))
        
        self.stdout.write(f'Visitor cards migrated: {cards_migrated}')
        
        # Summary
        self.stdout.write(self.style.SUCCESS(
            f'\nMigration completed successfully!\n'
            f'Visitors: {visitors_migrated}\n'
            f'Visit Requests: {requests_migrated}\n'
            f'Visitor Cards: {cards_migrated}\n'
        ))
        
        # Show MongoDB collection stats
        self.stdout.write('\nMongoDB Collections:')
        self.stdout.write(f'Visitors: {MongoVisitor.objects.count()}')
        self.stdout.write(f'Visit Requests: {MongoVisitRequest.objects.count()}')
        self.stdout.write(f'Visitor Cards: {MongoVisitorCard.objects.count()}')
