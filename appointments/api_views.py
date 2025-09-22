from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta, time
from .models import Appointment
from .serializers import (
    AppointmentSerializer, AppointmentCreateSerializer,
    AppointmentUpdateSerializer, AppointmentSummarySerializer,
    AvailableTimeSlotsSerializer
)
from doctors.models import Doctor
from patients.models import Patient


class AppointmentListCreateView(generics.ListCreateAPIView):
    """
    API view to list appointments or create a new appointment
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'doctor__user__first_name']
    ordering_fields = ['appointment_date', 'appointment_time', 'created_at']
    ordering = ['-appointment_date', 'appointment_time']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related('patient__user', 'doctor__user')
        
        # Role-based filtering
        if user.user_type == 'patient':
            try:
                patient = Patient.objects.get(user=user)
                queryset = queryset.filter(patient=patient)
            except Patient.DoesNotExist:
                return queryset.none()
        elif user.user_type == 'doctor':
            try:
                doctor = Doctor.objects.get(user=user)
                queryset = queryset.filter(doctor=doctor)
            except Doctor.DoesNotExist:
                return queryset.none()
        elif user.user_type in ['admin', 'staff']:
            # Admin and staff can see all appointments
            pass
        else:
            return queryset.none()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if date_from:
            queryset = queryset.filter(appointment_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(appointment_date__lte=date_to)
        
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        
        # Set the patient based on user type
        if user.user_type == 'patient':
            try:
                patient = Patient.objects.get(user=user)
                serializer.save(patient=patient)
            except Patient.DoesNotExist:
                raise permissions.PermissionDenied("Patient profile not found")
        elif user.user_type in ['admin', 'staff']:
            # Admin/staff can create appointments for any patient
            serializer.save()
        else:
            raise permissions.PermissionDenied("Only patients and admin can create appointments")


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete an appointment
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AppointmentUpdateSerializer
        return AppointmentSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related('patient__user', 'doctor__user')
        
        # Role-based filtering
        if user.user_type == 'patient':
            try:
                patient = Patient.objects.get(user=user)
                return queryset.filter(patient=patient)
            except Patient.DoesNotExist:
                return queryset.none()
        elif user.user_type == 'doctor':
            try:
                doctor = Doctor.objects.get(user=user)
                return queryset.filter(doctor=doctor)
            except Doctor.DoesNotExist:
                return queryset.none()
        elif user.user_type in ['admin', 'staff']:
            return queryset
        else:
            return queryset.none()
    
    def perform_destroy(self, instance):
        # Only allow cancellation, not deletion
        instance.status = 'cancelled'
        instance.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def available_time_slots(request, doctor_id):
    """
    API view to get available time slots for a doctor on a specific date
    """
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        date_str = request.GET.get('date')
        
        if not date_str:
            return Response({'error': 'Date parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if date is in the past
        if appointment_date < timezone.now().date():
            return Response({'error': 'Cannot book appointments for past dates'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate time slots (9 AM to 5 PM, 30-minute intervals)
        all_slots = []
        start_time = time(9, 0)  # 9:00 AM
        end_time = time(17, 0)   # 5:00 PM
        
        current_time = datetime.combine(appointment_date, start_time)
        end_datetime = datetime.combine(appointment_date, end_time)
        
        while current_time < end_datetime:
            all_slots.append(current_time.time())
            current_time += timedelta(minutes=30)
        
        # Get booked slots
        booked_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            status__in=['confirmed', 'pending']
        ).values_list('appointment_time', flat=True)
        
        # Filter out booked slots
        available_slots = [slot for slot in all_slots if slot not in booked_appointments]
        
        return Response({
            'date': appointment_date,
            'available_slots': available_slots,
            'total_slots': len(all_slots),
            'available_count': len(available_slots)
        })
        
    except Doctor.DoesNotExist:
        return Response({'error': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_appointment_status(request, appointment_id):
    """
    API view to update appointment status
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        new_status = request.data.get('status')
        
        # Check permissions
        user = request.user
        if user.user_type == 'patient' and appointment.patient.user != user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        elif user.user_type == 'doctor' and appointment.doctor.user != user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        elif user.user_type not in ['patient', 'doctor', 'admin', 'staff']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # Validate status
        valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled', 'rescheduled']
        if new_status not in valid_statuses:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        appointment.status = new_status
        appointment.save()
        
        return Response({
            'message': f'Appointment status updated to {new_status}',
            'appointment': AppointmentSerializer(appointment).data
        })
        
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def upcoming_appointments(request):
    """
    API view to get upcoming appointments for the current user
    """
    user = request.user
    today = timezone.now().date()
    
    if user.user_type == 'patient':
        try:
            patient = Patient.objects.get(user=user)
            appointments = Appointment.objects.filter(
                patient=patient,
                appointment_date__gte=today,
                status__in=['confirmed', 'pending']
            ).select_related('doctor__user').order_by('appointment_date', 'appointment_time')[:5]
        except Patient.DoesNotExist:
            appointments = []
    elif user.user_type == 'doctor':
        try:
            doctor = Doctor.objects.get(user=user)
            appointments = Appointment.objects.filter(
                doctor=doctor,
                appointment_date__gte=today,
                status__in=['confirmed', 'pending']
            ).select_related('patient__user').order_by('appointment_date', 'appointment_time')[:5]
        except Doctor.DoesNotExist:
            appointments = []
    else:
        appointments = []
    
    serializer = AppointmentSummarySerializer(appointments, many=True)
    return Response({'upcoming_appointments': serializer.data})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def appointment_statistics(request):
    """
    API view for appointment statistics
    """
    user = request.user
    
    if user.user_type not in ['admin', 'staff']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    today = timezone.now().date()
    
    stats = {
        'total_appointments': Appointment.objects.count(),
        'today_appointments': Appointment.objects.filter(appointment_date=today).count(),
        'pending_appointments': Appointment.objects.filter(status='pending').count(),
        'confirmed_appointments': Appointment.objects.filter(status='confirmed').count(),
        'completed_appointments': Appointment.objects.filter(status='completed').count(),
        'cancelled_appointments': Appointment.objects.filter(status='cancelled').count(),
    }
    
    return Response(stats)