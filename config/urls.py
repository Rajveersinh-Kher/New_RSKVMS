"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views as auth_views
from visitorapi import views as visitorapi_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views_django

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('visitorapi.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', auth_views.obtain_auth_token),
    path('', visitorapi_views.registration_user_login_view, name='home'),
    
    # Visitor management URLs
    path('register/', visitorapi_views.visitor_registration, name='visitor-registration'),
    path('register_visitor/', visitorapi_views.register_visitor, name='register-visitor-api'),
    path('search_visitors/', visitorapi_views.search_visitors, name='search-visitors-api'),
    path('export-visitors-excel/', visitorapi_views.export_visitors_excel, name='export_visitors_excel'),
    path('export-hos-visitors-excel/', visitorapi_views.export_hos_visitors_excel, name='export_hos_visitors_excel'),
    path('registration-login/', visitorapi_views.registration_user_login_view, name='registration-login'),
    path('registration-users-list/', visitorapi_views.registration_users_list, name='registration-users-list'),
    path('add-registration-user/', visitorapi_views.add_registration_user, name='add-registration-user'),
    path('delete-registration-user/', visitorapi_views.delete_registration_user, name='delete-registration-user'),
    path('hos-dashboard/', visitorapi_views.hos_dashboard_view, name='hos-dashboard'),
    path('hos-login/', visitorapi_views.hos_login_view, name='hos-login'),
    path('hos-password-reset/', visitorapi_views.hos_password_reset, name='hos-password-reset'),
    path('hos-password-reset-done/', visitorapi_views.hos_password_reset_done, name='hos-password-reset-done'),
    path('hos-reset/<uidb64>/<token>/', visitorapi_views.hos_password_reset_confirm, name='hos-password-reset-confirm'),
    path('hos-reset/done/', visitorapi_views.hos_password_reset_complete, name='hos-password-reset-complete'),
    path('registration-logout/', visitorapi_views.registration_logout_view, name='registration-logout'),
    path('hos-logout/', visitorapi_views.hos_logout_view, name='hos-logout'),
    path('print-card/', visitorapi_views.print_card_dashboard, name='print_card_dashboard'),
    path('print-card/step-2/', visitorapi_views.print_card_step2, name='print_card_step2'),
    path('print-card/mark-printed/', visitorapi_views.mark_cards_printed, name='mark_cards_printed'),
    path('print-card/clear-session/', visitorapi_views.clear_print_session, name='clear_print_session'),
    path('print-card/delete/<str:visit_id>/', visitorapi_views.delete_unprinted_visit_request, name='delete_unprinted_visit_request'),
    path('visitors/<str:visitor_id>/upload-photo/', visitorapi_views.upload_visitor_photo, name='upload_visitor_photo'),
    path('checkout/', visitorapi_views.checkout_visitor, name='checkout_visitor'),
    path('checkin/', visitorapi_views.checkin_visitor, name='checkin_visitor'),
    path('checkout-page/', visitorapi_views.checkout_page, name='checkout_page'),
    path('checked-in-visitors/', visitorapi_views.checked_in_visitors, name='checked_in_visitors'),
    path('manual-checkout/', visitorapi_views.manual_checkout_visitor, name='manual_checkout_visitor'),
    
    # Session-based auth and dashboard
    path('login/', visitorapi_views.login_view, name='login'),
    path('logout/', visitorapi_views.logout_view, name='logout'),
    path('dashboard/', visitorapi_views.hr_dashboard_view, name='hr-dashboard'),
    path('update-request/<str:request_id>/<str:action>/', visitorapi_views.update_request_status, name='update-request-status'),
    path('clear-sessions/', visitorapi_views.clear_all_sessions, name='clear-sessions'),
    
    # Password Reset URLs
    path('password_reset/', auth_views_django.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views_django.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views_django.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views_django.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Serve static files in production
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
