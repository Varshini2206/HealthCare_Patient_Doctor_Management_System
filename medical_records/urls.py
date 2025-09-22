from django.urls import path
from . import views

app_name = 'medical_records'

urlpatterns = [
    path('patient/<int:patient_id>/', views.patient_records, name='patient_records'),
    path('prescriptions/', views.prescriptions, name='prescriptions'),
    path('lab-results/', views.lab_results, name='lab_results'),
    path('vital-signs/', views.vital_signs, name='vital_signs'),
    path('allergies/', views.allergies, name='allergies'),
    path('history/', views.medical_history, name='medical_history'),
]