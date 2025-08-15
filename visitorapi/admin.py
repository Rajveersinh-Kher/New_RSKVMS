from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import HRUser, Visitor, VisitRequest, VisitorCard

@admin.register(HRUser)
class HRUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'department', 'employee_id', 'phone', 'is_active')
    list_filter = ('user_type', 'department', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'employee_id')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional Info', {'fields': ('user_type', 'department', 'employee_id', 'phone')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'user_type', 'department', 'employee_id', 'phone'),
        }),
    )

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'company', 'id_proof_type', 'created_at')
    list_filter = ('company', 'id_proof_type', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'company')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(VisitRequest)
class VisitRequestAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'host', 'purpose', 'visit_date', 'status', 'checkin_time', 'checkout_time')
    list_filter = ('status', 'visit_date', 'host__user_type', 'allow_mobile', 'allow_laptop')
    search_fields = ('visitor__first_name', 'visitor__last_name', 'host__username', 'purpose')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('visitor', 'host', 'purpose', 'other_purpose', 'visit_date', 'start_time', 'end_time')
        }),
        ('Status & Permissions', {
            'fields': ('status', 'allow_mobile', 'allow_laptop', 'approved_by')
        }),
        ('Reference Information', {
            'fields': ('requestedByEmployee', 'reference_employee_name', 'reference_employee_department', 'reference_purpose')
        }),
        ('Check-in/Check-out', {
            'fields': ('checkin_time', 'checkout_time', 'checkout_by_hr')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(VisitorCard)
class VisitorCardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'visit_request', 'status', 'issued_at', 'returned_at', 'printed')
    list_filter = ('status', 'printed', 'issued_at', 'returned_at')
    search_fields = ('card_number', 'visit_request__visitor__first_name', 'visit_request__visitor__last_name')
    readonly_fields = ('issued_at', 'qr_code_image')
    ordering = ('-issued_at',) 