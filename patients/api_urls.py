from django.urls import path
from . import api_views

# API URL patterns for patients app
app_name = 'patients_api'

urlpatterns = [
    # Patient CRUD endpoints
    path('', api_views.PatientListCreateView.as_view(), name='patient_list_create'),
    path('<int:pk>/', api_views.PatientDetailView.as_view(), name='patient_detail'),
    
    # Patient summary and search
    path('summary/', api_views.PatientSummaryListView.as_view(), name='patient_summary'),
    path('search/', api_views.patient_search, name='patient_search'),
    
    # Dashboard and statistics
    path('dashboard/stats/', api_views.patient_dashboard_stats, name='patient_dashboard_stats'),
]