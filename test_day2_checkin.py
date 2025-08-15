#!/usr/bin/env python
"""
Test script for Day 2+ check-in functionality
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

def test_day2_plus_checkins():
    """Test check-in functionality for day 2 and beyond"""
    print("Testing Day 2+ Check-in Functionality")
    print("=" * 50)
    
    try:
        # Get or create test visitor
        visitor, created = Visitor.objects.get_or_create(
            first_name="MultiDay",
            last_name="Visitor",
            phone="1234567890",
            company="Test Company",
            defaults={
                'id_proof_type': 'Passport',
                'id_proof_number': 'MULTI123'
            }
        )
        
        # Get or create test host
        host, created = HRUser.objects.get_or_create(
            username='multihost',
            defaults={
                'first_name': 'Multi',
                'last_name': 'Host',
                'email': 'multihost@example.com',
                'user_type': 'HR',
                'department': 'IT',
                'employee_id': 'MULTI001',
                'phone': '9876543210'
            }
        )
        
        # Create visit request for 5 days starting from yesterday
        visit_date = date.today() - timedelta(days=1)  # Start from yesterday
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
        print(f"Current date: {date.today()}")
        print(f"Current day number: {visit_request.get_current_day_number()}")
        
        # Test check-in for each day
        for day in range(1, 6):  # Test days 1-5
            print(f"\n{'='*30}")
            print(f"Testing Day {day}")
            print(f"{'='*30}")
            
            # Simulate the current day by temporarily changing visit_date
            original_visit_date = visit_request.visit_date
            simulated_visit_date = date.today() - timedelta(days=day-1)
            visit_request.visit_date = simulated_visit_date
            visit_request.save(update_fields=['visit_date'])
            
            print(f"Simulated visit date: {visit_request.visit_date}")
            print(f"Simulated current day number: {visit_request.get_current_day_number()}")
            print(f"Can check in today: {visit_request.can_check_in_today()}")
            print(f"Can check out today: {visit_request.can_check_out_today()}")
            
            # Test check-in
            if visit_request.can_check_in_today():
                checkin_field = visit_request.get_today_checkin_field()
                setattr(visit_request, checkin_field, timezone.now())
                visit_request.save(update_fields=[checkin_field])
                print(f"✓ Checked in successfully for day {day}")
                print(f"  Check-in time: {getattr(visit_request, checkin_field)}")
                
                # Test check-out
                if visit_request.can_check_out_today():
                    checkout_field = visit_request.get_today_checkout_field()
                    setattr(visit_request, checkout_field, timezone.now())
                    visit_request.save(update_fields=[checkout_field])
                    print(f"✓ Checked out successfully for day {day}")
                    print(f"  Check-out time: {getattr(visit_request, checkout_field)}")
                else:
                    print("✗ Cannot check out (should be able to)")
            else:
                print("✗ Cannot check in today")
            
            # Restore original visit_date
            visit_request.visit_date = original_visit_date
            visit_request.save(update_fields=['visit_date'])
        
        # Display all day data
        print(f"\n{'='*50}")
        print("FINAL RESULTS - All Day Check-in/Check-out Data:")
        print(f"{'='*50}")
        for day in range(1, 11):
            checkin_field = f'day_{day}_checkin'
            checkout_field = f'day_{day}_checkout'
            checkin_time = getattr(visit_request, checkin_field)
            checkout_time = getattr(visit_request, checkout_field)
            
            if checkin_time or checkout_time:
                print(f"Day {day}: Check-in: {checkin_time}, Check-out: {checkout_time}")
            else:
                print(f"Day {day}: No data")
        
        print(f"\n✓ Day 2+ functionality test completed successfully!")
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_day2_plus_checkins() 