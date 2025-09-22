from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('dashboard/', views.patient_dashboard, name='dashboard'),
    path('profile/', views.patient_profile, name='profile'),
    path('appointments/', views.patient_appointments, name='appointments'),
    path('appointments/<int:appointment_id>/', views.patient_appointment_detail, name='appointment_detail'),
    path('medical-history/', views.medical_history, name='medical_history'),
    path('medical-records/', views.medical_history, name='medical_records'),  # Alias for template consistency
    path('documents/', views.patient_documents, name='documents'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('export-medical-records/', views.export_medical_records, name='export_medical_records'),
    path('request-medical-records/', views.request_medical_records, name='request_medical_records'),
    
    # Document management
    path('documents/view/<str:document_name>/', views.view_document, name='view_document'),
    path('documents/download/<str:document_name>/', views.download_document, name='download_document'),
    path('documents/upload/', views.upload_document, name='upload_document'),
]