from django.urls import path
from healthcare_project import analytics_views

app_name = 'dashboard'

urlpatterns = [
    path('analytics/', analytics_views.analytics_dashboard, name='analytics'),
    path('patient-analytics/', analytics_views.patient_analytics, name='patient_analytics'),
    path('doctor-analytics/', analytics_views.doctor_analytics, name='doctor_analytics'),
    
    # HTMX endpoints
    path('live-stats/', analytics_views.live_stats, name='live_stats'),
    path('chart-data/', analytics_views.chart_data, name='chart_data'),
    path('recent-activity/', analytics_views.recent_activity, name='recent_activity'),
]