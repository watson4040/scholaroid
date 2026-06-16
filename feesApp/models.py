from django.db import models
from studentsApp.models import Student
from accountsApp.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum
import uuid

class FeeStructure(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.amount}"

class Invoice(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('overdue', 'Overdue'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='invoices')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def balance(self):
        return self.amount_due - self.amount_paid

    def __str__(self):
        return f"Invoice for {self.student.user.username} - {self.fee_structure.name}"

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    receipt_number = models.CharField(max_length=50, unique=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"RCPT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
        # Update invoice amount_paid and status
        total_paid = self.invoice.payments.aggregate(Sum('amount'))['amount__sum'] or 0
        self.invoice.amount_paid = total_paid
        if self.invoice.amount_paid >= self.invoice.amount_due:
            self.invoice.status = 'paid'
        elif self.invoice.amount_paid > 0:
            self.invoice.status = 'partial'
        else:
            self.invoice.status = 'pending'
        self.invoice.save()
        # Send email to parent
        parent_email = self.invoice.student.parent.user.email if self.invoice.student.parent else None
        if parent_email:
            send_mail(
                subject='Payment Received – Scholaroid',
                message=f"""
Dear Parent,

A payment of {self.amount} has been received for {self.invoice.student.user.username}'s invoice.

Receipt Number: {self.receipt_number}
Invoice: {self.invoice.fee_structure.name}
Amount Paid: {self.amount}
Remaining Balance: {self.invoice.balance()}

Thank you,
Scholaroid School
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[parent_email],
                fail_silently=True,
            )

    def __str__(self):
        return f"Payment {self.receipt_number} - {self.amount}"