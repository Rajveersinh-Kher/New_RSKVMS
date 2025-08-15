from django.db import migrations, models

def migrate_old_checkin_data(apps, schema_editor):
    """Migrate existing checkin/checkout data to day_1 fields"""
    VisitRequest = apps.get_model('visitorapi', 'VisitRequest')
    
    # Get all visit requests with old checkin/checkout data
    visit_requests = VisitRequest.objects.filter(
        models.Q(checkin_time__isnull=False) | models.Q(checkout_time__isnull=False)
    )
    
    for visit_request in visit_requests:
        # Migrate checkin_time to day_1_checkin if not already set
        if visit_request.checkin_time and not visit_request.day_1_checkin:
            visit_request.day_1_checkin = visit_request.checkin_time
        
        # Migrate checkout_time to day_1_checkout if not already set
        if visit_request.checkout_time and not visit_request.day_1_checkout:
            visit_request.day_1_checkout = visit_request.checkout_time
        
        visit_request.save(update_fields=['day_1_checkin', 'day_1_checkout'])

def reverse_migrate_old_checkin_data(apps, schema_editor):
    """Reverse migration - move day_1 data back to old fields"""
    VisitRequest = apps.get_model('visitorapi', 'VisitRequest')
    
    visit_requests = VisitRequest.objects.filter(
        models.Q(day_1_checkin__isnull=False) | models.Q(day_1_checkout__isnull=False)
    )
    
    for visit_request in visit_requests:
        if visit_request.day_1_checkin and not visit_request.checkin_time:
            visit_request.checkin_time = visit_request.day_1_checkin
        
        if visit_request.day_1_checkout and not visit_request.checkout_time:
            visit_request.checkout_time = visit_request.day_1_checkout
        
        visit_request.save(update_fields=['checkin_time', 'checkout_time'])

class Migration(migrations.Migration):

    dependencies = [
        ('visitorapi', '0019_visitrequest_day_10_checkin_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_old_checkin_data, reverse_migrate_old_checkin_data),
    ] 