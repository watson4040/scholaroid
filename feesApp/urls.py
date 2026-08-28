from django.urls import path
from . import views

urlpatterns = [
    path('parent/invoices/', views.parent_invoices, name='parent_invoices'),
    path('student/invoices/', views.student_invoices, name='student_invoices'),
    path('admin/report/', views.admin_invoice_report, name='admin_fee_report'),
]