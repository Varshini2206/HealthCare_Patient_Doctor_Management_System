from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views

# API URL patterns for accounts app
app_name = 'accounts_api'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', api_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', api_views.logout_view, name='logout'),
    path('auth/register/', api_views.UserRegistrationView.as_view(), name='register'),
    
    # User profile endpoints
    path('profile/', api_views.UserProfileView.as_view(), name='profile'),
    path('profile/user/', api_views.user_profile_view, name='user_profile'),
    path('profile/change-password/', api_views.ChangePasswordView.as_view(), name='change_password'),
]