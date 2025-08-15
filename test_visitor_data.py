#!/usr/bin/env python
"""
Test script to verify visitor data integrity
Run this script to check if there are any issues with visitor data in the database
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from visitorapi.models import VisitRequest, Visitor, VisitorCard

def test_visitor_data_integrity():
    """Test visitor data integrity"""
    print("Testing visitor data integrity...")
    
    # Get all approved requests
    approved_requests = VisitRequest.objects.select_related('visitor').filter(status='APPROVED').order_by('-created_at')
    
    print(f"Total approved requests: {approved_requests.count()}")
    
    # Check each request
    for i, req in enumerate(approved_requests):
        visitor = req.visitor
        print(f"Request {i+1}: ID={req.id}, Visitor={visitor.first_name} {visitor.last_name} (Visitor ID: {visitor.id})")
        
        # Check if visitor data is consistent
        if not visitor.first_name or not visitor.last_name:
            print(f"  WARNING: Missing visitor name data!")
        
        # Check if there are duplicate visitors with same name
        same_name_visitors = Visitor.objects.filter(
            first_name=visitor.first_name,
            last_name=visitor.last_name
        )
        if same_name_visitors.count() > 1:
            print(f"  WARNING: Multiple visitors with same name: {visitor.first_name} {visitor.last_name}")
            for v in same_name_visitors:
                print(f"    Visitor ID: {v.id}, Email: {v.email}, Company: {v.company}")
    
    # Check for any orphaned records
    print("\nChecking for orphaned records...")
    
    # Check for VisitRequests without visitors
    orphaned_requests = VisitRequest.objects.filter(visitor__isnull=True)
    if orphaned_requests.exists():
        print(f"WARNING: Found {orphaned_requests.count()} VisitRequests without visitors")
    
    # Check for VisitorCards without VisitRequests
    orphaned_cards = VisitorCard.objects.filter(visit_request__isnull=True)
    if orphaned_cards.exists():
        print(f"WARNING: Found {orphaned_cards.count()} VisitorCards without VisitRequests")
    
    print("\nData integrity check completed.")

if __name__ == "__main__":
    test_visitor_data_integrity() 

for vr in VisitRequest.objects.all():
    print(f"ID: {vr.id}, day_1_checkin: {vr.day_1_checkin}, day_1_checkout: {vr.day_1_checkout}, day_2_checkin: {vr.day_2_checkin}, day_2_checkout: {vr.day_2_checkout}, day_3_checkin: {vr.day_3_checkin}, day_3_checkout: {vr.day_3_checkout}") 