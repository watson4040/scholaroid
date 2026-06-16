from django.urls import path, include
from . import views
from .views import change_password
from studentsApp.views import enrollment_request, enrollment_success   # <-- correct import

urlpatterns = [
    # ... your existing paths ...
    path('enroll/', enrollment_request, name='enroll'),
    path('enroll/success/', enrollment_success, name='enrollment_success'),
]