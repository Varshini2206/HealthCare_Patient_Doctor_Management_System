from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_documentation(request):
    """
    API documentation endpoint
    """
    api_docs = {
        "Healthcare Patient Management System API": {
            "version": "1.0",
            "description": "RESTful API for healthcare patient management system",
            "base_url": f"{request.build_absolute_uri('/api/v1/')}",
            "endpoints": {
                "Authentication": {
                    "login": "POST /api/v1/accounts/auth/login/",
                    "register": "POST /api/v1/accounts/auth/register/",
                    "refresh": "POST /api/v1/accounts/auth/refresh/",
                    "logout": "POST /api/v1/accounts/auth/logout/",
                    "profile": "GET/PUT /api/v1/accounts/profile/",
                    "change_password": "POST /api/v1/accounts/profile/change-password/"
                },
                "Patients": {
                    "list_create": "GET/POST /api/v1/patients/",
                    "detail": "GET/PUT/DELETE /api/v1/patients/{id}/",
                    "summary": "GET /api/v1/patients/summary/",
                    "search": "GET /api/v1/patients/search/?q=search_term",
                    "dashboard_stats": "GET /api/v1/patients/dashboard/stats/"
                },
                "Doctors": {
                    "list_create": "GET/POST /api/v1/doctors/",
                    "detail": "GET/PUT/DELETE /api/v1/doctors/{id}/",
                    "summary": "GET /api/v1/doctors/summary/",
                    "search": "GET /api/v1/doctors/search/?q=search_term",
                    "specializations": "GET /api/v1/doctors/specializations/",
                    "dashboard_stats": "GET /api/v1/doctors/dashboard/stats/",
                    "toggle_availability": "POST /api/v1/doctors/toggle-availability/"
                },
                "Appointments": {
                    "list_create": "GET/POST /api/v1/appointments/",
                    "detail": "GET/PUT/DELETE /api/v1/appointments/{id}/",
                    "update_status": "POST /api/v1/appointments/{id}/status/",
                    "upcoming": "GET /api/v1/appointments/upcoming/",
                    "available_slots": "GET /api/v1/appointments/doctors/{doctor_id}/available-slots/?date=YYYY-MM-DD",
                    "statistics": "GET /api/v1/appointments/statistics/"
                }
            },
            "authentication": {
                "type": "JWT (JSON Web Token)",
                "header": "Authorization: Bearer <token>",
                "note": "Include access token in Authorization header for protected endpoints"
            },
            "sample_requests": {
                "login": {
                    "method": "POST",
                    "url": "/api/v1/accounts/auth/login/",
                    "payload": {
                        "username": "your_username",
                        "password": "your_password"
                    }
                },
                "create_appointment": {
                    "method": "POST",
                    "url": "/api/v1/appointments/",
                    "headers": {"Authorization": "Bearer <access_token>"},
                    "payload": {
                        "patient": 1,
                        "doctor": 1,
                        "appointment_date": "2025-09-22",
                        "appointment_time": "10:30:00",
                        "appointment_type": "consultation",
                        "reason": "Regular checkup"
                    }
                }
            }
        }
    }
    
    return Response(api_docs)