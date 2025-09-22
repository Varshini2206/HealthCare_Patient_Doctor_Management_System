from rest_framework import serializers
from .models import Doctor
from accounts.serializers import UserSerializer


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for Doctor model
    """
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'user', 'doctor_id', 'license_number', 'specialization',
            'qualifications', 'experience_years', 'consultation_fee',
            'working_hours', 'bio', 'is_available', 'is_verified',
            'avatar', 'full_name', 'rating', 'created_at'
        ]
        read_only_fields = ['id', 'doctor_id', 'created_at', 'full_name', 'rating']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    
    def get_rating(self, obj):
        # In a real implementation, this would calculate from reviews
        return 4.5  # Placeholder rating


class DoctorCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a doctor
    """
    class Meta:
        model = Doctor
        fields = [
            'license_number', 'specialization', 'qualifications',
            'experience_years', 'consultation_fee', 'working_hours',
            'bio', 'avatar'
        ]


class DoctorUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating doctor information
    """
    class Meta:
        model = Doctor
        fields = [
            'specialization', 'qualifications', 'experience_years',
            'consultation_fee', 'working_hours', 'bio', 'avatar',
            'is_available'
        ]


class DoctorSummarySerializer(serializers.ModelSerializer):
    """
    Minimal serializer for doctor summaries
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'doctor_id', 'full_name', 'specialization',
            'experience_years', 'consultation_fee', 'is_available'
        ]
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()


class DoctorPublicSerializer(serializers.ModelSerializer):
    """
    Public serializer for doctor information (for patient searches)
    """
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'doctor_id', 'full_name', 'specialization',
            'qualifications', 'experience_years', 'consultation_fee',
            'bio', 'is_available', 'avatar_url'
        ]
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None