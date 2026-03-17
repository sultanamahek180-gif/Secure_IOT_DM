from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    # ✅ Organization URLs (ADD THESE)
    path('organizations/', views.organization_list, name='organization_list'),
    path('organizations/create/', views.organization_create, name='organization_create'),
    path('organizations/update/<int:org_id>/', views.organization_update, name='organization_update'),
    path('organizations/delete/<int:org_id>/', views.organization_delete, name='organization_delete'),
    path('confirm-create/', views.confirm_create, name='confirm_create'),
    path('devices/', views.device_list, name='device_list'),
    path('devices/create/', views.device_create, name='device_create'),
    path('devices/update/<uuid:device_id>/', views.device_update, name='device_update'),
    path('devices/delete/<uuid:device_id>/', views.device_delete, name='device_delete'),
    
    # Device Data URLs
path(
    'devices/<uuid:device_id>/data/',
    views.devicedata_list,
    name='devicedata_list'
),
path(
    'devices/<uuid:device_id>/data/create/',
    views.devicedata_create,
    name='devicedata_create'
),
path(
    'devices/data/update/<uuid:data_id>/',
    views.devicedata_update,
    name='devicedata_update'
),
path(
    'devices/data/delete/<uuid:data_id>/',
    views.devicedata_delete,
    name='devicedata_delete'
),
path('alerts/create/', views.alert_create, name='alert_create'),
path('alerts/', views.alert_list, name='alert_list'),
path('alerts/update/<uuid:alert_id>/', views.alert_update, name='alert_update'),
path('alerts/delete/<uuid:alert_id>/', views.alert_delete, name='alert_delete'),
path('device-access/create/', views.deviceaccess_create, name='deviceaccess_create'),
path('device-access/', views.deviceaccess_list, name='deviceaccess_list'),

path('device-access/update/<uuid:access_id>/', views.deviceaccess_update, name='deviceaccess_update'),
path('device-access/delete/<uuid:access_id>/', views.deviceaccess_delete, name='deviceaccess_delete'),
path('alerts/<uuid:device_id>/', views.alert_list, name='alert_list'),
]