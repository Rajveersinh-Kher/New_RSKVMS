# Multi-Day Check-in/Check-out Implementation

## Overview

This implementation adds support for multi-day visitor check-in and check-out functionality to the visitor management system. Visitors can now check in and check out multiple times over their approved visit period (up to 10 days).

## Key Features

1. **Multi-day Support**: Visitors can check in and check out each day during their approved visit period
2. **Day-specific Tracking**: Each day's check-in and check-out times are stored separately
3. **Automatic Day Calculation**: The system automatically determines which day of the visit period it is
4. **Validation**: Prevents check-in/check-out outside the valid visit period
5. **Backward Compatibility**: Existing single-day check-in/check-out data is migrated to day 1

## Database Changes

### New Fields Added to VisitRequest Model

The following 20 new fields were added to track check-in/check-out for each day:

```python
# Day 1-10 check-in/check-out fields
day_1_checkin = models.DateTimeField(null=True, blank=True)
day_1_checkout = models.DateTimeField(null=True, blank=True)
day_2_checkin = models.DateTimeField(null=True, blank=True)
day_2_checkout = models.DateTimeField(null=True, blank=True)
# ... continues for days 3-10
day_10_checkin = models.DateTimeField(null=True, blank=True)
day_10_checkout = models.DateTimeField(null=True, blank=True)
```

### Migration Strategy

1. **Migration 0019**: Added all new day-specific fields
2. **Migration 0020**: Migrated existing check-in/check-out data to day_1 fields

## New Model Methods

### VisitRequest Model Methods

```python
def get_current_day_number(self):
    """Get the current day number based on visit_date and valid_upto"""
    # Returns 1-10 for valid days, 0 for before visit, -1 for after visit

def can_check_in_today(self):
    """Check if visitor can check in today"""
    # Returns True if today is within the valid visit period

def can_check_out_today(self):
    """Check if visitor can check out today (must be checked in first)"""
    # Returns True if checked in today but not checked out

def get_today_checkin_field(self):
    """Get the checkin field name for today"""
    # Returns field name like 'day_1_checkin'

def get_today_checkout_field(self):
    """Get the checkout field name for today"""
    # Returns field name like 'day_1_checkout'

def migrate_old_checkin_data(self):
    """Migrate old checkin/checkout data to day_1 fields"""
    # Moves existing checkin_time/checkout_time to day_1 fields
```

## API Endpoints

### New Check-in Endpoint

**URL**: `/checkin/`
**Method**: POST
**Parameters**: `qr_data` (QR code data)
**Response**: JSON with success status and check-in time

### Updated Check-out Endpoint

**URL**: `/checkout/`
**Method**: POST
**Parameters**: `qr_data` (QR code data)
**Response**: JSON with success status and check-out time

## Frontend Changes

### Updated Checkout Page

The checkout page (`templates/checkout.html`) now includes:

1. **Two separate sections**: One for check-in and one for check-out
2. **Different colored buttons**: Green for check-in, orange for check-out
3. **Separate QR input fields**: One for each action
4. **Enhanced styling**: Better visual separation between sections

### Key Features

- **Dual functionality**: Single page handles both check-in and check-out
- **Visual distinction**: Different colors and styling for each action
- **Responsive design**: Works on mobile and desktop devices
- **Real-time feedback**: Shows success/error messages for each action

## Excel Export Updates

### New Column Structure

The Excel export now includes day-specific columns at the end:

```
...existing fields..., Day 1 Check In, Day 1 Check Out, Day 2 Check In, Day 2 Check Out, ..., Day 10 Check In, Day 10 Check Out
```

### Migration of Existing Data

- Existing `checkin_time` data → `Day 1 Check In`
- Existing `checkout_time` data → `Day 1 Check Out`
- Empty columns for unused days

## Usage Examples

### Scenario 1: Single Day Visit
- Visitor gets approved for 1 day
- Data appears in `Day 1 Check In` and `Day 1 Check Out`
- Days 2-10 remain empty

### Scenario 2: Multi-day Visit
- Visitor gets approved for 5 days (valid_upto = visit_date + 4 days)
- Each day's check-in/check-out is tracked separately
- Days 6-10 remain empty

### Scenario 3: Daily Check-in/Check-out
1. **Day 1**: Visitor checks in → `day_1_checkin` populated
2. **Day 1**: Visitor checks out → `day_1_checkout` populated
3. **Day 2**: Visitor checks in → `day_2_checkin` populated
4. **Day 2**: Visitor checks out → `day_2_checkout` populated
5. **And so on...**

## Validation Rules

### Check-in Validation
- Must be within valid visit period (visit_date to valid_upto)
- Cannot check in twice on the same day
- Day number must be 1-10

### Check-out Validation
- Must be within valid visit period
- Must be checked in for the current day
- Cannot check out twice on the same day
- Day number must be 1-10

## Backward Compatibility

### Existing Data
- All existing check-in/check-out data is automatically migrated to day 1
- No data loss occurs during migration
- Old fields (`checkin_time`, `checkout_time`) remain for compatibility

### API Compatibility
- Existing endpoints continue to work
- New endpoints are additive, not breaking changes
- QR code format remains the same

## Testing

### Test Script
A test script (`test_multi_day_checkin.py`) is provided to verify functionality:

```bash
python test_multi_day_checkin.py
```

### Test Scenarios
1. **Single day check-in/check-out**
2. **Multi-day check-in/check-out**
3. **Validation of visit periods**
4. **Day calculation accuracy**
5. **Data migration verification**

## Deployment Notes

### Migration Steps
1. Run `python manage.py makemigrations`
2. Run `python manage.py migrate`
3. Verify data migration with test script
4. Update frontend templates
5. Test check-in/check-out functionality

### Configuration
- No additional configuration required
- Uses existing QR code system
- Compatible with existing user roles and permissions

## Future Enhancements

### Potential Improvements
1. **Email notifications** for daily check-ins/check-outs
2. **Dashboard statistics** showing daily visitor counts
3. **Reporting features** for multi-day visit analysis
4. **Mobile app integration** for easier QR scanning
5. **Bulk operations** for managing multiple visitors

### Scalability Considerations
- Current implementation supports up to 10 days
- Can be extended to support more days if needed
- Database queries are optimized for day-specific lookups
- Excel export handles large datasets efficiently

## Troubleshooting

### Common Issues

1. **"Cannot check in today" error**
   - Check if visit period is valid
   - Verify current date is within visit_date to valid_upto range

2. **"Already checked in today" error**
   - Visitor has already checked in for the current day
   - Use check-out instead

3. **"Cannot check out today" error**
   - Visitor must check in before checking out
   - Check if already checked out for the day

4. **Excel export missing data**
   - Verify migration completed successfully
   - Check if day-specific fields are populated

### Debug Information
- Use the test script to verify functionality
- Check Django admin for field values
- Review migration logs for any issues
- Verify QR code format and parsing

## Support

For issues or questions regarding this implementation:
1. Check the test script output
2. Review migration logs
3. Verify database field values
4. Test with sample data
5. Contact development team for assistance 