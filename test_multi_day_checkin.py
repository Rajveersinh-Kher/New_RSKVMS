#!/usr/bin/env python
"""
Test script for multi-day check-in/check-out functionality
"""
import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from visitorapi.models import VisitRequest, Visitor, HRUser, VisitorCard
from django.utils import timezone

def test_multi_day_functionality():
    """Test the multi-day check-in/check-out functionality"""
    print("Testing Multi-Day Check-in/Check-out Functionality")
    print("=" * 50)
    
    # Create test data
    try:
        # Get or create test visitor
        visitor, created = Visitor.objects.get_or_create(
            first_name="Test",
            last_name="Visitor",
            phone="1234567890",
            company="Test Company",
            defaults={
                'id_proof_type': 'Passport',
                'id_proof_number': 'TEST123'
            }
        )
        
        # Get or create test host
        host, created = HRUser.objects.get_or_create(
            username='testhost',
            defaults={
                'first_name': 'Test',
                'last_name': 'Host',
                'email': 'testhost@example.com',
                'user_type': 'HR',
                'department': 'IT',
                'employee_id': 'HOST001',
                'phone': '9876543210'
            }
        )
        
        # Create visit request for 5 days
        visit_date = date.today()
        valid_upto = visit_date + timedelta(days=4)  # 5 days total
        
        visit_request, created = VisitRequest.objects.get_or_create(
            visitor=visitor,
            host=host,
            visit_date=visit_date,
            defaults={
                'purpose': 'Testing multi-day functionality',
                'end_time': '17:30:00',
                'status': 'APPROVED',
                'valid_upto': valid_upto
            }
        )
        
        print(f"Created visit request: {visit_request}")
        print(f"Visit date: {visit_request.visit_date}")
        print(f"Valid until: {visit_request.valid_upto}")
        print(f"Current day number: {visit_request.get_current_day_number()}")
        
        # Test day-specific methods
        print(f"\nTesting day-specific methods:")
        print(f"Can check in today: {visit_request.can_check_in_today()}")
        print(f"Can check out today: {visit_request.can_check_out_today()}")
        print(f"Today's checkin field: {visit_request.get_today_checkin_field()}")
        print(f"Today's checkout field: {visit_request.get_today_checkout_field()}")
        
        # Test check-in for day 1
        print(f"\nTesting check-in for day 1:")
        if visit_request.can_check_in_today():
            checkin_field = visit_request.get_today_checkin_field()
            setattr(visit_request, checkin_field, timezone.now())
            visit_request.save(update_fields=[checkin_field])
            print(f"✓ Checked in successfully at: {getattr(visit_request, checkin_field)}")
        else:
            print("✗ Cannot check in today")
        
        # Test check-out for day 1
        print(f"\nTesting check-out for day 1:")
        if visit_request.can_check_out_today():
            checkout_field = visit_request.get_today_checkout_field()
            setattr(visit_request, checkout_field, timezone.now())
            visit_request.save(update_fields=[checkout_field])
            print(f"✓ Checked out successfully at: {getattr(visit_request, checkout_field)}")
        else:
            print("✗ Cannot check out today")
        
        # Test check-in for day 2 (simulate next day)
        print(f"\nTesting check-in for day 2 (simulated):")
        # Temporarily modify visit_date to simulate day 2
        original_visit_date = visit_request.visit_date
        visit_request.visit_date = visit_date - timedelta(days=1)
        visit_request.save(update_fields=['visit_date'])
        
        print(f"Simulated current day number: {visit_request.get_current_day_number()}")
        print(f"Can check in today: {visit_request.can_check_in_today()}")
        print(f"Can check out today: {visit_request.can_check_out_today()}")
        
        if visit_request.can_check_in_today():
            checkin_field = visit_request.get_today_checkin_field()
            setattr(visit_request, checkin_field, timezone.now())
            visit_request.save(update_fields=[checkin_field])
            print(f"✓ Checked in successfully for day 2 at: {getattr(visit_request, checkin_field)}")
        else:
            print("✗ Cannot check in for day 2")
        
        # Restore original visit_date
        visit_request.visit_date = original_visit_date
        visit_request.save(update_fields=['visit_date'])
        
        # Display all day data
        print(f"\nAll day check-in/check-out data:")
        for day in range(1, 11):
            checkin_field = f'day_{day}_checkin'
            checkout_field = f'day_{day}_checkout'
            checkin_time = getattr(visit_request, checkin_field)
            checkout_time = getattr(visit_request, checkout_field)
            
            if checkin_time or checkout_time:
                print(f"Day {day}: Check-in: {checkin_time}, Check-out: {checkout_time}")
        
        print(f"\n✓ Multi-day functionality test completed successfully!")
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multi_day_functionality() 