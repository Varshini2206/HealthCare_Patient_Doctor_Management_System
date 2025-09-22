"""
URL configuration for healthcare_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .api_docs import api_documentation

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    
    # Service redirects with authentication
    path('services/appointments/', views.service_appointments, name='service_appointments'),
    path('services/medical-records/', views.service_medical_records, name='service_medical_records'),
    path('services/prescriptions/', views.service_prescriptions, name='service_prescriptions'),
    path('services/telemedicine/', views.service_telemedicine, name='service_telemedicine'),
    
    path('accounts/', include('accounts.urls')),
    path('patients/', include('patients.urls')),
    path('doctors/', include('doctors.urls')),
    path('appointments/', include('appointments.urls')),
    # Temporarily disabled until migrations are fixed
    # path('medical-records/', include('medical_records.urls')),
    # Dashboard URLs - temporarily disabled due to medical_records dependency
    # path('dashboard/', include('dashboard.urls')),
    path('allauth/', include('allauth.urls')),
    
    # API endpoints
    path('api/v1/', api_documentation, name='api_docs'),
    path('api/v1/accounts/', include('accounts.api_urls')),
    path('api/v1/patients/', include('patients.api_urls')),
    path('api/v1/doctors/', include('doctors.api_urls')),
    path('api/v1/appointments/', include('appointments.api_urls')),
    # path('api/v1/medical-records/', include('medical_records.api_urls')),  # To be added later
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
