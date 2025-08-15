# Visitor Management System

A comprehensive Django-based visitor management system with multi-user roles, QR code generation, and automated email notifications.

## 🚀 Features

### Core Functionality
- **Multi-User Role Management**: HR, Registration, and HOS (Head of Security) users
- **Visitor Registration**: Complete visitor information capture with photo upload
- **Visit Request Processing**: Approval workflow with status tracking
- **QR Code Generation**: Automatic QR code generation for visitor cards
- **Check-in/Check-out System**: Real-time visitor tracking
- **Email Notifications**: Automated email alerts for password resets and visit updates

### User Interfaces
- **HR Dashboard**: Complete visitor management interface
- **Registration Portal**: Streamlined visitor registration
- **HOS Dashboard**: Security-focused interface
- **Checkout Interface**: QR code scanning for visitor checkout
- **Admin Interface**: Django admin for system management

### Technical Features
- **REST API**: Full API with DRF for integration
- **Token Authentication**: Secure API access
- **Responsive Design**: Mobile-friendly Bootstrap interface
- **Excel Export**: Data export functionality
- **Session Management**: Secure session handling

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd visitor_management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   # Copy example environment file
   cp env.example .env
   # Edit .env with your settings
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main application: http://127.0.0.1:8000/
   - Admin interface: http://127.0.0.1:8000/admin/

## 📧 Email Configuration

### Gmail Setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Update settings in `config/settings.py`:
   ```python
   EMAIL_HOST_USER = 'your-email@gmail.com'
   EMAIL_HOST_PASSWORD = 'your-app-password'
   ```

## 🔐 Security Configuration

### Production Settings
Update `config/settings.py` for production:

```python
DEBUG = False
SECRET_KEY = 'your-secure-secret-key'
ALLOWED_HOSTS = ['your-domain.com']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Generate Secure Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 📊 API Documentation

### Authentication
```bash
# Get token
curl -X POST http://localhost:8000/api-token-auth/ \
  -d "username=admin&password=your_password"

# Use token
curl -H "Authorization: Token your_token_here" \
  http://localhost:8000/api/visitors/
```

### Available Endpoints
- `GET/POST /api/visitors/` - Visitor management
- `GET/POST /api/visit-requests/` - Visit request management
- `GET/POST /api/visitor-cards/` - Visitor card management
- `GET/POST /api/hr-users/` - HR user management

## 🎨 Customization

### Branding
- Update logo in `static/img/godrej_logo.png`
- Modify colors in `static/theme.css`
- Update company name in templates

### Email Templates
- Customize email templates in `templates/registration/`
- Update email subjects and content in views

## 🚀 Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker (Recommended)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 📝 Usage Guide

### For HR Users
1. Login to HR dashboard
2. Review pending visit requests
3. Approve/reject requests
4. Generate visitor cards
5. Monitor check-ins/check-outs

### For Registration Users
1. Login to registration portal
2. Register new visitors
3. Capture visitor information
4. Submit for approval

### For HOS Users
1. Login to HOS dashboard
2. Monitor security-related activities
3. Manage visitor access

## 🔧 Maintenance

### Database Backup
```bash
python manage.py dumpdata > backup.json
```

### Static Files
```bash
python manage.py collectstatic
```

### Logs
Monitor application logs for errors and performance issues.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Django Version**: 5.2.4 