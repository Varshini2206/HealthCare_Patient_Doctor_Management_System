from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from .models import Doctor
from .serializers import (
    DoctorSerializer, DoctorCreateSerializer, 
    DoctorUpdateSerializer, DoctorSummarySerializer, DoctorPublicSerializer
)


class DoctorListCreateView(generics.ListCreateAPIView):
    """
    API view to list all doctors or create a new doctor
    """
    queryset = Doctor.objects.filter(is_verified=True).select_related('user')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'doctor_id']
    ordering_fields = ['user__first_name', 'user__last_name', 'years_of_experience']
    ordering = ['user__first_name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DoctorCreateSerializer
        elif self.request.user.user_type == 'patient':
            return DoctorPublicSerializer
        return DoctorSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by specialization if provided
        specialization = self.request.query_params.get('specialization', None)
        if specialization:
            queryset = queryset.filter(specializations__name__icontains=specialization)
        
        # Filter by availability if provided
        available = self.request.query_params.get('available', None)
        if available is not None:
            queryset = queryset.filter(is_available_for_appointments=available.lower() == 'true')
        
        return queryset
    
    def perform_create(self, serializer):
        # Only admin can create doctor records
        if self.request.user.user_type != 'admin':
            raise permissions.PermissionDenied("Only admin can create doctor records")
        
        serializer.save(user=self.request.user)


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a doctor
    """
    queryset = Doctor.objects.select_related('user')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DoctorUpdateSerializer
        elif self.request.user.user_type == 'patient':
            return DoctorPublicSerializer
        return DoctorSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Role-based filtering
        if self.request.user.user_type == 'doctor':
            # Doctors can only access their own record
            return queryset.filter(user=self.request.user)
        elif self.request.user.user_type in ['admin', 'staff']:
            # Admin and staff can access all doctor records
            return queryset
        elif self.request.user.user_type == 'patient':
            # Patients can only see verified doctors
            return queryset.filter(is_verified=True)
        else:
            return queryset.none()
    
    def perform_destroy(self, instance):
        # Only admin can delete doctors
        if self.request.user.user_type != 'admin':
            raise permissions.PermissionDenied("Only admin can delete doctor records")
        
        # Soft delete - mark as not available
        instance.is_available = False
        instance.save()


class DoctorSummaryListView(generics.ListAPIView):
    """
    API view for doctor summaries (minimal data for lists/selects)
    """
    queryset = Doctor.objects.filter(is_verified=True, is_available_for_appointments=True).select_related('user')
    serializer_class = DoctorSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name']
    ordering = ['user__first_name', 'user__last_name']


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def doctor_dashboard_stats(request):
    """
    API view for doctor dashboard statistics
    """
    user = request.user
    
    if user.user_type == 'doctor':
        try:
            doctor = Doctor.objects.get(user=user)
            from appointments.models import Appointment
            from medical_records.models import MedicalRecord
            
            today = timezone.now().date()
            
            stats = {
                'total_appointments': Appointment.objects.filter(doctor=doctor).count(),
                'today_appointments': Appointment.objects.filter(
                    doctor=doctor,
                    appointment_date=today
                ).count(),
                'pending_appointments': Appointment.objects.filter(
                    doctor=doctor,
                    status='pending'
                ).count(),
                'total_patients': Appointment.objects.filter(
                    doctor=doctor
                ).values('patient').distinct().count(),
                'medical_records_created': MedicalRecord.objects.filter(doctor=doctor).count(),
            }
            
            return Response(stats)
        except Doctor.DoesNotExist:
            return Response({'error': 'Doctor profile not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def doctor_search(request):
    """
    API view for doctor search functionality
    """
    query = request.GET.get('q', '')
    specialization = request.GET.get('specialization', '')
    
    if len(query) < 2 and not specialization:
        return Response({'results': []})
    
    queryset = Doctor.objects.filter(is_verified=True, is_available_for_appointments=True)
    
    if query:
        queryset = queryset.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(doctor_id__icontains=query)
        )
    
    if specialization:
        queryset = queryset.filter(specializations__name__icontains=specialization)
    
    doctors = queryset.select_related('user')[:20]
    serializer = DoctorPublicSerializer(doctors, many=True)
    return Response({'results': serializer.data})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def specializations_list(request):
    """
    API view to get list of all specializations
    """
    specializations = Doctor.objects.filter(
        is_verified=True, 
        is_available=True
    ).values_list('specialization', flat=True).distinct().order_by('specialization')
    
    return Response({'specializations': list(specializations)})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_availability(request):
    """
    API view for doctors to toggle their availability status
    """
    if request.user.user_type != 'doctor':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        doctor = Doctor.objects.get(user=request.user)
        doctor.is_available = not doctor.is_available
        doctor.save()
        
        return Response({
            'message': f"Availability updated to {'Available' if doctor.is_available else 'Not Available'}",
            'is_available': doctor.is_available
        })
    except Doctor.DoesNotExist:
        return Response({'error': 'Doctor profile not found'}, status=status.HTTP_404_NOT_FOUND)