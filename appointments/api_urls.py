from django.urls import path
from . import api_views

# API URL patterns for appointments app
app_name = 'appointments_api'

urlpatterns = [
    # Appointment CRUD endpoints
    path('', api_views.AppointmentListCreateView.as_view(), name='appointment_list_create'),
    path('<int:pk>/', api_views.AppointmentDetailView.as_view(), name='appointment_detail'),
    
    # Appointment management
    path('<int:appointment_id>/status/', api_views.update_appointment_status, name='update_status'),
    path('upcoming/', api_views.upcoming_appointments, name='upcoming_appointments'),
    
    # Doctor availability
    path('doctors/<int:doctor_id>/available-slots/', api_views.available_time_slots, name='available_slots'),
    
    # Statistics
    path('statistics/', api_views.appointment_statistics, name='appointment_statistics'),
]