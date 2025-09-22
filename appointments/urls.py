from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/', views.book_appointment, name='book'),
    path('confirm/<int:appointment_id>/', views.confirm_appointment, name='confirm'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel'),
    path('reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule'),
    path('history/', views.appointment_history, name='history'),
]