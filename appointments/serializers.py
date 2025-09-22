from rest_framework import serializers
from .models import Appointment
from patients.serializers import PatientSummarySerializer
from doctors.serializers import DoctorSummarySerializer


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Appointment model
    """
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    patient = PatientSummarySerializer(read_only=True)
    doctor = DoctorSummarySerializer(read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'appointment_id', 'patient', 'doctor', 'patient_name', 'doctor_name',
            'appointment_date', 'appointment_time', 'appointment_type',
            'reason', 'status', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'appointment_id', 'created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
    
    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name()


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating appointments
    """
    class Meta:
        model = Appointment
        fields = [
            'patient', 'doctor', 'appointment_date', 'appointment_time',
            'appointment_type', 'reason'
        ]
    
    def validate(self, attrs):
        # Check if doctor is available
        if not attrs['doctor'].is_available:
            raise serializers.ValidationError("Selected doctor is not available")
        
        # Check for appointment conflicts (same doctor, date, time)
        existing = Appointment.objects.filter(
            doctor=attrs['doctor'],
            appointment_date=attrs['appointment_date'],
            appointment_time=attrs['appointment_time'],
            status__in=['confirmed', 'pending']
        ).exists()
        
        if existing:
            raise serializers.ValidationError("This time slot is already booked")
        
        return attrs


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating appointments
    """
    class Meta:
        model = Appointment
        fields = [
            'appointment_date', 'appointment_time', 'appointment_type',
            'reason', 'status', 'notes'
        ]
    
    def validate(self, attrs):
        instance = self.instance
        
        # If rescheduling, check for conflicts
        if ('appointment_date' in attrs or 'appointment_time' in attrs):
            new_date = attrs.get('appointment_date', instance.appointment_date)
            new_time = attrs.get('appointment_time', instance.appointment_time)
            
            existing = Appointment.objects.filter(
                doctor=instance.doctor,
                appointment_date=new_date,
                appointment_time=new_time,
                status__in=['confirmed', 'pending']
            ).exclude(id=instance.id).exists()
            
            if existing:
                raise serializers.ValidationError("This time slot is already booked")
        
        return attrs


class AppointmentSummarySerializer(serializers.ModelSerializer):
    """
    Minimal serializer for appointment summaries
    """
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'appointment_id', 'patient_name', 'doctor_name',
            'appointment_date', 'appointment_time', 'status', 'appointment_type'
        ]
    
    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
    
    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name()


class AvailableTimeSlotsSerializer(serializers.Serializer):
    """
    Serializer for available time slots
    """
    date = serializers.DateField()
    time_slots = serializers.ListField(
        child=serializers.TimeField(),
        read_only=True
    )