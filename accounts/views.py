from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
import uuid
from .forms import CustomUserCreationForm, CustomUserChangeForm, UserProfileForm
from .models import UserProfile
from patients.models import Patient
from doctors.models import Doctor

User = get_user_model()


class RegisterView(CreateView):
    """
    User registration view
    """
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    
    def get_success_url(self):
        """Redirect based on user type after successful registration"""
        if self.object.user_type == 'patient':
            return reverse_lazy('patients:dashboard')
        elif self.object.user_type == 'doctor':
            return reverse_lazy('doctors:dashboard')
        else:
            return reverse_lazy('home')
    
    def form_valid(self, form):
        # Create the user first
        response = super().form_valid(form)
        user = self.object
        
        # Create role-specific profiles in a separate transaction
        try:
            with transaction.atomic():
                if user.user_type == 'patient':
                    Patient.objects.get_or_create(user=user)
                elif user.user_type == 'doctor':
                    # Generate unique identifiers for doctor
                    doctor_id = f"DOC{str(uuid.uuid4())[:8].upper()}"
                    medical_license = f"ML{str(uuid.uuid4())[:10].upper()}"
                    
                    # Ensure uniqueness
                    while Doctor.objects.filter(doctor_id=doctor_id).exists():
                        doctor_id = f"DOC{str(uuid.uuid4())[:8].upper()}"
                    while Doctor.objects.filter(medical_license_number=medical_license).exists():
                        medical_license = f"ML{str(uuid.uuid4())[:10].upper()}"
                    
                    Doctor.objects.get_or_create(
                        user=user,
                        defaults={
                            'doctor_id': doctor_id,
                            'medical_license_number': medical_license,
                            'years_of_experience': 0,
                            'is_verified': False
                        }
                    )
            
            # Log in the user after the transaction completes
            user = authenticate(
                self.request,
                username=user.email,  # Using email as username
                password=form.cleaned_data.get('password1')
            )
            if user:
                login(self.request, user)
                messages.success(
                    self.request, 
                    f'Welcome! Your {user.get_user_type_display().lower()} account has been created successfully.'
                )
        except Exception as e:
            messages.error(self.request, f'Error creating profile: {str(e)}. Please contact support.')
        
        return response
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register'
        return context


class ProfileView(LoginRequiredMixin, DetailView):
    """
    User profile detail view
    """
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'user'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Profile'
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        
        # Get role-specific profile
        user = self.request.user
        if user.user_type == 'patient':
            try:
                context['patient_profile'] = user.patient_profile
            except:
                context['patient_profile'] = None
        elif user.user_type == 'doctor':
            try:
                context['doctor_profile'] = user.doctor_profile
            except:
                context['doctor_profile'] = None
        
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    User profile update view
    """
    model = User
    form_class = CustomUserChangeForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Profile'
        return context


class ProfilePreferencesView(LoginRequiredMixin, UpdateView):
    """
    User profile preferences update view
    """
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile_preferences.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Preferences updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Profile Preferences'
        return context


@login_required
def dashboard_view(request):
    """
    Dashboard view - redirects based on user type
    """
    user = request.user
    
    if user.user_type == 'patient':
        return redirect('patients:dashboard')
    elif user.user_type == 'doctor':
        return redirect('doctors:dashboard')
    elif user.user_type in ['admin', 'staff']:
        return redirect('admin:index')
    else:
        return render(request, 'accounts/dashboard.html', {
            'title': 'Dashboard',
            'user': user
        })


def home_view(request):
    """
    Home page view
    """
    if request.user.is_authenticated:
        return dashboard_view(request)
    
    return render(request, 'home.html', {
        'title': 'Healthcare Management System'
    })


class UserListView(LoginRequiredMixin, ListView):
    """
    User list view for admin users
    """
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.user_type in ['admin', 'staff']:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = User.objects.all().select_related('profile')
        user_type = self.request.GET.get('user_type')
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        return queryset.order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'User Management'
        context['user_types'] = User.USER_TYPE_CHOICES
        context['selected_type'] = self.request.GET.get('user_type', '')
        return context
