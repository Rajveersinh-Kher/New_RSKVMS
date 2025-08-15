# Data Clearing Commands for RSK Visitor Management System

This document explains how to use the data clearing commands to remove visitor data from your hybrid SQLite + MongoDB system.

## Overview

Your system uses:
- **SQLite**: HR users and authentication (preserved during clearing)
- **MongoDB Atlas**: Visitor data, visit requests, and visitor cards
- **Media Files**: Visitor photos and QR code images

## Available Commands

### 1. Clear All Data (`clear_all_data`)

**Purpose**: Completely removes all visitor-related data from both databases and optionally media files.

**Usage**:
```bash
# Clear everything with confirmation
python manage.py clear_all_data

# Force clear without confirmation
python manage.py clear_all_data --force

# Clear only SQLite data
python manage.py clear_all_data --sqlite-only

# Clear only MongoDB data
python manage.py clear_all_data --mongodb-only

# Clear data AND media files
python manage.py clear_all_data --media-files

# Combine options
python manage.py clear_all_data --mongodb-only --media-files
```

**What it deletes**:
- All visitors from both databases
- All visit requests from both databases
- All visitor cards from both databases
- Optionally: All visitor photos and QR code images

**What it preserves**:
- HR user accounts and authentication data
- User sessions and permissions

### 2. Clear Only Requests (`clear_requests`)

**Purpose**: Removes only visit requests and visitor cards while preserving visitor data.

**Usage**:
```bash
# Clear requests with confirmation
python manage.py clear_requests

# Force clear without confirmation
python manage.py clear_requests --force

# Clear only SQLite requests
python manage.py clear_requests --sqlite-only

# Clear only MongoDB requests
python manage.py clear_requests --mongodb-only
```

**What it deletes**:
- All visit requests from both databases
- All visitor cards from both databases

**What it preserves**:
- Visitor information (names, contact details, photos)
- HR user accounts and authentication data

### 3. Clear All Users (`clear_all_users`)

**Purpose**: Deletes ALL users including HR users, superusers, HOS users, and registration users.

**Usage**:
```bash
# Clear all users with confirmation
python manage.py clear_all_users

# Force clear without confirmation
python manage.py clear_all_users --force

# Keep one emergency superuser
python manage.py clear_all_users --keep-superuser

# Clear users AND media files
python manage.py clear_all_users --media-files
```

**What it deletes**:
- ALL user accounts (HR, superusers, HOS, registration)
- All user sessions
- All user permissions and groups
- Optionally: All media files

**What it preserves**:
- Optionally: One emergency superuser account

### 4. Nuclear Reset (`nuclear_reset`)

**Purpose**: Complete system destruction - clears EVERYTHING including all users and data.

**Usage**:
```bash
# Nuclear reset with confirmation
python manage.py nuclear_reset

# Force nuclear reset without confirmation
python manage.py nuclear_reset --force

# Nuclear reset but keep emergency superuser
python manage.py nuclear_reset --keep-superuser
```

**What it deletes**:
- ALL users (HR, superusers, HOS, registration)
- ALL visitors from both databases
- ALL visit requests from both databases
- ALL visitor cards from both databases
- ALL media files (photos, QR codes)
- ALL user sessions
- ALL permissions and groups

**What it preserves**:
- Optionally: One emergency superuser account

## Safety Features

1. **Confirmation Required**: By default, all commands require you to type "YES" to confirm
2. **Data Counts**: Shows current data counts before deletion
3. **Transaction Safety**: SQLite deletions use database transactions for safety
4. **Error Handling**: Continues operation even if one database fails
5. **Detailed Logging**: Shows exactly what was deleted and any errors

## When to Use Each Command

### Use `clear_all_data` when:
- Starting fresh with a new system
- Removing all visitor history
- Cleaning up after testing
- Want to completely reset the system

### Use `clear_requests` when:
- Want to keep visitor information
- Only need to clear visit history
- Planning to reuse existing visitors
- Testing new request workflows

## Examples

### Scenario 1: Complete System Reset (Keep Users)
```bash
python manage.py clear_all_data --media-files
```
This will remove everything except HR users, giving you a clean slate for data.

### Scenario 2: Keep Visitors, Clear History
```bash
python manage.py clear_requests
```
This keeps all visitor information but removes all visit requests and cards.

### Scenario 3: Clear Only MongoDB (if SQLite is corrupted)
```bash
python manage.py clear_all_data --sqlite-only
```
This clears only the MongoDB data, useful if you have database-specific issues.

### Scenario 4: Delete All Users (Complete User Reset)
```bash
python manage.py clear_all_users --force
```
This deletes ALL users but keeps the system structure intact.

### Scenario 5: Nuclear Reset (Complete System Destruction)
```bash
python manage.py nuclear_reset --force
```
This destroys EVERYTHING - complete system reset. Use only when you want to start completely fresh.

## Important Notes

⚠️ **WARNING**: These commands permanently delete data. There is no undo!

🔒 **HR Users Preserved**: Your HR user accounts and authentication will remain intact.

🔄 **Restart Required**: After clearing data, you may need to restart your Django application.

📊 **Backup First**: Consider backing up your data before running these commands.

## Troubleshooting

### If you get permission errors:
- Ensure you're running the command from the project directory
- Check that your Django environment is properly configured
- Verify MongoDB connection settings

### If MongoDB connection fails:
- Check your `MONGODB_URI` environment variable
- Verify network connectivity to MongoDB Atlas
- Check if your IP is whitelisted in MongoDB Atlas

### If media files can't be deleted:
- Check file permissions in the media directory
- Ensure the Django process has write access
- Try running with elevated permissions if necessary

## Support

If you encounter issues with these commands:
1. Check the Django logs for error messages
2. Verify your database connections
3. Ensure all required packages are installed
4. Test with a small dataset first
