from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from crispy_forms.bootstrap import FormActions
from .models import UserProfile

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user registration form
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, required=True)
    phone_number = forms.CharField(max_length=17, required=False)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'user_type', 
                 'phone_number', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'email',
            Row(
                Column('user_type', css_class='form-group col-md-6 mb-0'),
                Column('phone_number', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-0'),
                Column('password2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            FormActions(
                Submit('submit', 'Register', css_class='btn-primary btn-lg')
            )
        )
        
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.user_type = self.cleaned_data['user_type']
        user.phone_number = self.cleaned_data['phone_number']
        
        # Generate username from email
        if not user.username:
            user.username = self.cleaned_data['email'].split('@')[0]
            # Ensure username is unique
            base_username = user.username
            counter = 1
            while User.objects.filter(username=user.username).exists():
                user.username = f"{base_username}{counter}"
                counter += 1
        
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.get_or_create(user=user)
        
        return user


class CustomUserChangeForm(UserChangeForm):
    """
    Custom user profile update form
    """
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 
                 'date_of_birth', 'address', 'avatar')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'email',
            Row(
                Column('phone_number', css_class='form-group col-md-6 mb-0'),
                Column('date_of_birth', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'address',
            'avatar',
            FormActions(
                Submit('submit', 'Update Profile', css_class='btn-primary')
            )
        )
        
        # Remove password field
        if 'password' in self.fields:
            del self.fields['password']
        
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name != 'avatar':
                field.widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    """
    Extended user profile form
    """
    class Meta:
        model = UserProfile
        fields = ['emergency_contact_name', 'emergency_contact_phone', 
                 'emergency_contact_relationship', 'medical_alerts', 
                 'preferred_language', 'receive_notifications', 
                 'receive_email_reminders', 'receive_sms_reminders']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'emergency_contact_name',
            Row(
                Column('emergency_contact_phone', css_class='form-group col-md-6 mb-0'),
                Column('emergency_contact_relationship', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'medical_alerts',
            'preferred_language',
            Row(
                Column('receive_notifications', css_class='form-group col-md-4 mb-0'),
                Column('receive_email_reminders', css_class='form-group col-md-4 mb-0'),
                Column('receive_sms_reminders', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            FormActions(
                Submit('submit', 'Update Preferences', css_class='btn-success')
            )
        )
        
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'