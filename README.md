HealthCare Patient Management System

A comprehensive healthcare management platform built with Django that facilitates seamless interaction between patients and doctors. This system provides a complete solution for appointment scheduling, medical record management, prescription handling, and patient care coordination.

Deployment Link : https://healthcare-patient-doctor-management.onrender.com/

Render Free Tier Database Limitation

This project is deployed on **Render's free tier**. The associated PostgreSQL database has a limited lifespan and will be **automatically deleted 30 days after its creation date**.

* **Creation Date:** Sep 30, 2025

Project Overview

The HealthCare Patient Management System is designed to streamline healthcare operations by providing separate dashboards for patients and doctors. Patients can book appointments, view their medical history, manage prescriptions, and access important documents. Doctors can manage their schedules, view patient profiles, provide feedback, and maintain comprehensive medical records.

Technologies Used

- Backend: Django 4.2.7 (Python Web Framework)
- Frontend: HTML5, CSS3, Bootstrap 5.3
- Database: SQLite (Development) / PostgreSQL (Production Ready)
- Authentication: Django's built-in authentication system
- Forms: Django Crispy Forms for enhanced form rendering
- APIs: Django REST Framework for API endpoints
- File Handling: Django's file upload and management system
- Styling: Font Awesome icons, Custom CSS animations

How to Run This Project:

Prerequisites:

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

Installation Steps:

1. Clone the Repository
   ```bash
   git clone <repository-url>
   cd HealthCare-Patient-Management-System
   ```

2. Create Virtual Environment
   ```bash
   python -m venv healthcare_env
   ```

3. Activate Virtual Environment
   
   On Windows:
   ```bash
   healthcare_env\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source healthcare_env/bin/activate
   ```

4. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure Environment Variables
   - Create a `.env` file in the root directory
   - Add necessary environment variables (database credentials, email settings, etc.)
   - Note: Never commit the `.env` file to version control

6. Run Database Migrations
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. Create Superuser (Optional)
   ```bash
   python manage.py createsuperuser
   ```

8. Collect Static Files (Production)
   ```bash
   python manage.py collectstatic
   ```

9. Run the Development Server
   ```bash
   python manage.py runserver
   ```

10. Access the Application
    - Open your web browser
    - Navigate to `http://127.0.0.1:8000/`
    - Register as a patient or doctor to explore the platform

Additional Setup (Optional):

- Load Sample Data: Use the provided fixtures or create sample data through the admin panel
- Configure Email Backend: Set up SMTP settings for email notifications
- Database Configuration: Configure PostgreSQL for production deployment
- Security Settings: Review and configure security settings for production use

Support:

For any issues or questions, please contact the development team or create an issue in the repository.

Medical Disclaimer:

This software is intended for educational and demonstration purposes. It should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for medical decisions.




Built with ❤️ for better healthcare management
