from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import Patient
from .serializers import (
    PatientSerializer, PatientCreateSerializer, 
    PatientUpdateSerializer, PatientSummarySerializer
)


class PatientListCreateView(generics.ListCreateAPIView):
    """
    API view to list all patients or create a new patient
    """
    queryset = Patient.objects.filter(is_active=True).select_related('user')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'patient_id', 'user__email']
    ordering_fields = ['user__first_name', 'user__last_name', 'created_at', 'date_of_birth']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PatientCreateSerializer
        return PatientSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Role-based filtering
        if self.request.user.user_type == 'patient':
            # Patients can only see their own record
            return queryset.filter(user=self.request.user)
        elif self.request.user.user_type == 'doctor':
            # Doctors can see all patients (for appointments/medical records)
            return queryset
        elif self.request.user.user_type in ['admin', 'staff']:
            # Admin and staff can see all patients
            return queryset
        else:
            return queryset.none()
    
    def perform_create(self, serializer):
        # Only admin/staff can create patient records
        if self.request.user.user_type not in ['admin', 'staff']:
            raise permissions.PermissionDenied("Only admin/staff can create patient records")
        
        # In a real scenario, this would be handled differently
        # For now, assume the user is already created
        serializer.save(user=self.request.user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a patient
    """
    queryset = Patient.objects.select_related('user')
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PatientUpdateSerializer
        return PatientSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Role-based filtering
        if self.request.user.user_type == 'patient':
            # Patients can only access their own record
            return queryset.filter(user=self.request.user)
        elif self.request.user.user_type in ['doctor', 'admin', 'staff']:
            # Healthcare providers can access all patient records
            return queryset
        else:
            return queryset.none()
    
    def perform_destroy(self, instance):
        # Soft delete - mark as inactive instead of deleting
        instance.is_active = False
        instance.save()


class PatientSummaryListView(generics.ListAPIView):
    """
    API view for patient summaries (minimal data for lists/selects)
    """
    queryset = Patient.objects.filter(is_active=True).select_related('user')
    serializer_class = PatientSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'patient_id']
    ordering = ['user__first_name', 'user__last_name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Role-based filtering
        if self.request.user.user_type == 'patient':
            return queryset.filter(user=self.request.user)
        elif self.request.user.user_type in ['doctor', 'admin', 'staff']:
            return queryset
        else:
            return queryset.none()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def patient_dashboard_stats(request):
    """
    API view for patient dashboard statistics
    """
    user = request.user
    
    if user.user_type == 'patient':
        try:
            patient = Patient.objects.get(user=user)
            from appointments.models import Appointment
            from medical_records.models import MedicalRecord, Prescription
            
            stats = {
                'total_appointments': Appointment.objects.filter(patient=patient).count(),
                'upcoming_appointments': Appointment.objects.filter(
                    patient=patient, 
                    status='confirmed',
                    appointment_date__gte=timezone.now().date()
                ).count(),
                'total_medical_records': MedicalRecord.objects.filter(patient=patient).count(),
                'active_prescriptions': Prescription.objects.filter(
                    patient=patient, 
                    status='active'
                ).count(),
            }
            
            return Response(stats)
        except Patient.DoesNotExist:
            return Response({'error': 'Patient profile not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def patient_search(request):
    """
    API view for patient search functionality
    """
    if request.user.user_type not in ['doctor', 'admin', 'staff']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    query = request.GET.get('q', '')
    if len(query) < 2:
        return Response({'results': []})
    
    patients = Patient.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query) |
        Q(patient_id__icontains=query) |
        Q(user__email__icontains=query),
        is_active=True
    ).select_related('user')[:20]
    
    serializer = PatientSummarySerializer(patients, many=True)
    return Response({'results': serializer.data})