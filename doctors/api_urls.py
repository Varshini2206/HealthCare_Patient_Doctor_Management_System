from django.urls import path
from . import api_views

# API URL patterns for doctors app
app_name = 'doctors_api'

urlpatterns = [
    # Doctor CRUD endpoints
    path('', api_views.DoctorListCreateView.as_view(), name='doctor_list_create'),
    path('<int:pk>/', api_views.DoctorDetailView.as_view(), name='doctor_detail'),
    
    # Doctor summary and search
    path('summary/', api_views.DoctorSummaryListView.as_view(), name='doctor_summary'),
    path('search/', api_views.doctor_search, name='doctor_search'),
    path('specializations/', api_views.specializations_list, name='specializations_list'),
    
    # Dashboard and statistics
    path('dashboard/stats/', api_views.doctor_dashboard_stats, name='doctor_dashboard_stats'),
    path('toggle-availability/', api_views.toggle_availability, name='toggle_availability'),
]