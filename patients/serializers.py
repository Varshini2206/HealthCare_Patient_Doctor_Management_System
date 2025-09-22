from rest_framework import serializers
from .models import Patient
from accounts.serializers import UserSerializer


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient model
    """
    user = UserSerializer(read_only=True)
    age = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 'user', 'patient_id', 'date_of_birth', 'gender', 
            'blood_type', 'height', 'weight', 'address', 
            'emergency_contact_name', 'emergency_contact_phone',
            'insurance_provider', 'insurance_policy_number',
            'medical_history', 'allergies', 'current_medications',
            'is_active', 'age', 'full_name', 'created_at'
        ]
        read_only_fields = ['id', 'patient_id', 'created_at', 'age', 'full_name']
    
    def get_age(self, obj):
        return obj.age
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()


class PatientCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a patient
    """
    class Meta:
        model = Patient
        fields = [
            'date_of_birth', 'gender', 'blood_type', 'height', 'weight',
            'address', 'emergency_contact_name', 'emergency_contact_phone',
            'insurance_provider', 'insurance_policy_number',
            'medical_history', 'allergies', 'current_medications'
        ]


class PatientUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating patient information
    """
    class Meta:
        model = Patient
        fields = [
            'date_of_birth', 'gender', 'blood_type', 'height', 'weight',
            'address', 'emergency_contact_name', 'emergency_contact_phone',
            'insurance_provider', 'insurance_policy_number',
            'medical_history', 'allergies', 'current_medications'
        ]


class PatientSummarySerializer(serializers.ModelSerializer):
    """
    Minimal serializer for patient summaries
    """
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = ['id', 'patient_id', 'full_name', 'age', 'gender', 'blood_type']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    
    def get_age(self, obj):
        return obj.age