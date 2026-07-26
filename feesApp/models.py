from decimal import Decimal
import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from accountsApp.models import User
from studentsApp.models import Student


# ==========================================================
# PAYMENT METHODS
# ==========================================================

class PaymentMethod(models.TextChoices):
    CASH = "Cash", "Cash"
    BANK = "Bank", "Bank Transfer"
    MOBILE = "Mobile Money", "Mobile Money"
    POS = "POS", "POS Machine"
    CHEQUE = "Cheque", "Cheque"


# ==========================================================
# FEE CATEGORIES
# ==========================================================

class FeeCategory(models.TextChoices):
    TUITION = "Tuition", "Tuition"
    TRANSPORT = "Transport", "Transport"
    BOARDING = "Boarding", "Boarding"
    UNIFORM = "Uniform", "Uniform"
    EXAM = "Exam", "Exam"
    ACTIVITIES = "Activities", "Activities"
    PTA = "PTA", "PTA"
    REGISTRATION = "Registration", "Registration"
    OTHER = "Other", "Other"


# ==========================================================
# FEE STRUCTURE
# ==========================================================

class FeeStructure(models.Model):

    name = models.CharField(max_length=100)

    category = models.CharField(
        max_length=30,
        choices=FeeCategory.choices,
        default=FeeCategory.TUITION,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    due_date = models.DateField()

    description = models.TextField(
        blank=True,
    )

    active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.category})"


# ==========================================================
# DISCOUNTS
# ==========================================================

class Discount(models.Model):

    name = models.CharField(
        max_length=100,
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    active = models.BooleanField(
        default=True,
    )

    description = models.TextField(
        blank=True,
    )

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"


# ==========================================================
# SCHOLARSHIPS
# ==========================================================

class Scholarship(models.Model):

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="scholarship",
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    reason = models.TextField(
        blank=True,
    )

    active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"{self.student} Scholarship"


# ==========================================================
# STUDENT EXTRA SERVICES
# ==========================================================

class StudentService(models.Model):

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="services",
    )

    uses_transport = models.BooleanField(
        default=False,
    )

    transport_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    boarding = models.BooleanField(
        default=False,
    )

    boarding_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    uniform_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    other_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    def total_extra_fees(self):

        return (
            self.transport_fee
            + self.boarding_fee
            + self.uniform_fee
            + self.other_fee
        )

    def __str__(self):
        return str(self.student)
    # ==========================================================
# INVOICE
# ==========================================================

class Invoice(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("partial", "Partially Paid"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="invoices",
    )

    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.CASCADE,
    )

    discount = models.ForeignKey(
        Discount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    amount_due = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.fee_structure.name}"

    @property
    def balance(self):
        return self.amount_due - self.amount_paid

    @property
    def is_paid(self):
        return self.balance <= Decimal("0.00")

    @property
    def is_overdue(self):
        if self.status == "paid":
            return False

        if self.due_date:
            return timezone.now().date() > self.due_date

        return False

    def calculate_total(self):

        total = Decimal(self.fee_structure.amount)

        # Student extra services
        try:
            services = self.student.services
            total += services.total_extra_fees()
        except StudentService.DoesNotExist:
            pass

        # Scholarship
        try:
            scholarship = self.student.scholarship

            if scholarship.active:
                total -= (
                    total
                    * Decimal(scholarship.percentage)
                    / Decimal("100")
                )

        except Scholarship.DoesNotExist:
            pass

        # Discount
        if self.discount and self.discount.active:
            total -= (
                total
                * Decimal(self.discount.percentage)
                / Decimal("100")
            )

        if total < 0:
            total = Decimal("0.00")

        return total.quantize(Decimal("0.01"))

    def update_status(self):

        if self.amount_paid >= self.amount_due:

            self.status = "paid"

        elif self.amount_paid > 0:

            self.status = "partial"

        elif self.is_overdue:

            self.status = "overdue"

        else:

            self.status = "pending"

    def save(self, *args, **kwargs):

        if not self.due_date:
            self.due_date = self.fee_structure.due_date

        self.amount_due = self.calculate_total()

        self.update_status()

        super().save(*args, **kwargs)
# ==========================================================
# PAYMENT
# ==========================================================

class Payment(models.Model):

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
    )

    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
    )

    transaction_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    payment_date = models.DateTimeField(
        auto_now_add=True,
    )

    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_payments",
    )

    notes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["-payment_date"]

    def __str__(self):
        return f"{self.receipt_number} - {self.amount}"


    def generate_receipt_number(self):

        return (
            f"RCPT-"
            f"{timezone.now().strftime('%Y%m%d')}-"
            f"{uuid.uuid4().hex[:6].upper()}"
        )


    def send_parent_receipt(self):

        student = self.invoice.student

        try:
            parent_email = student.parent.user.email

        except Exception:
            parent_email = None


        if parent_email:

            send_mail(

                subject="Payment Receipt - Scholaroid",

                message=f"""
Dear Parent,

We have received a payment for:

Pupil:
{student.user.get_full_name()}

Amount Paid:
{self.amount}

Receipt Number:
{self.receipt_number}

Payment Method:
{self.payment_method}

Remaining Balance:
{self.invoice.balance}

Thank you for choosing our school.

Scholaroid School Management System
""",

                from_email=settings.DEFAULT_FROM_EMAIL,

                recipient_list=[
                    parent_email
                ],

                fail_silently=True,
            )


    def update_invoice(self):

        invoice = self.invoice


        total_paid = invoice.payments.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")


        invoice.amount_paid = total_paid

        invoice.update_status()

        invoice.save(
            update_fields=[
                "amount_paid",
                "status",
                "updated_at",
            ]
        )


    def save(self, *args, **kwargs):

        if not self.receipt_number:

            self.receipt_number = (
                self.generate_receipt_number()
            )


        super().save(*args, **kwargs)


        self.update_invoice()

        self.send_parent_receipt()


# ==========================================================
# PAYMENT AUDIT LOG
# ==========================================================

class PaymentAuditLog(models.Model):

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )


    action = models.CharField(
        max_length=100,
    )


    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
    )


    details = models.TextField(
        blank=True,
    )


    def __str__(self):

        return (
            f"{self.action} - "
            f"{self.payment.receipt_number}"
        )
# ==========================================================
# SCHOOL EXPENSES
# ==========================================================

class ExpenseCategory(models.TextChoices):

    SALARY = "Salary", "Salary"
    UTILITIES = "Utilities", "Utilities"
    SUPPLIES = "Supplies", "Supplies"
    MAINTENANCE = "Maintenance", "Maintenance"
    TRANSPORT = "Transport", "Transport"
    OTHER = "Other", "Other"



class Expense(models.Model):

    title = models.CharField(
        max_length=150,
    )

    category = models.CharField(
        max_length=30,
        choices=ExpenseCategory.choices,
        default=ExpenseCategory.OTHER,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    expense_date = models.DateField(
        default=timezone.now,
    )

    description = models.TextField(
        blank=True,
    )

    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )


    class Meta:
        ordering = ["-expense_date"]


    def __str__(self):

        return f"{self.title} - {self.amount}"



# ==========================================================
# FINANCIAL REPORT HELPERS
# ==========================================================

class FinancialReport(models.Model):

    month = models.PositiveIntegerField()

    year = models.PositiveIntegerField()


    total_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )


    total_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )


    profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )


    generated_at = models.DateTimeField(
        auto_now_add=True,
    )


    def calculate_profit(self):

        self.profit = (
            self.total_income
            -
            self.total_expenses
        )

        return self.profit


    def save(self, *args, **kwargs):

        self.calculate_profit()

        super().save(*args, **kwargs)


    def __str__(self):

        return (
            f"{self.month}/{self.year} "
            f"Financial Report"
        )



# ==========================================================
# SCHOOL SUBSCRIPTION SYSTEM
# ==========================================================

class SubscriptionPlan(models.Model):

    PLAN_CHOICES = (

        (
            "basic",
            "Basic Private School",
        ),

        (
            "premium",
            "Premium Private School",
        ),

        (
            "enterprise",
            "Enterprise School",
        ),

    )


    name = models.CharField(
        max_length=50,
        choices=PLAN_CHOICES,
    )


    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )


    yearly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )


    max_pupils = models.PositiveIntegerField(
        default=500,
    )


    description = models.TextField(
        blank=True,
    )


    active = models.BooleanField(
        default=True,
    )


    def __str__(self):

        return self.get_name_display()



class SchoolSubscription(models.Model):


    STATUS = (

        (
            "active",
            "Active",
        ),

        (
            "expired",
            "Expired",
        ),

        (
            "cancelled",
            "Cancelled",
        ),

    )


    school_name = models.CharField(
        max_length=150,
    )


    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
    )


    start_date = models.DateField(
        default=timezone.now,
    )


    expiry_date = models.DateField()


    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="active",
    )


    auto_disable = models.BooleanField(
        default=True,
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
    )


    def check_expiry(self):

        if timezone.now().date() > self.expiry_date:

            self.status = "expired"

            self.save(
                update_fields=[
                    "status"
                ]
            )

            return True

        return False



    def is_active(self):

        self.check_expiry()

        return self.status == "active"



    def __str__(self):

        return (
            f"{self.school_name} - "
            f"{self.status}"
        )
# ==========================================================
# SUBSCRIPTION PAYMENT HISTORY
# ==========================================================

class SubscriptionPayment(models.Model):

    subscription = models.ForeignKey(
        SchoolSubscription,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    payment_reference = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
    )

    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK,
    )

    paid_on = models.DateTimeField(
        auto_now_add=True,
    )

    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )


    def save(self, *args, **kwargs):

        if not self.payment_reference:

            self.payment_reference = (
                f"SUB-{uuid.uuid4().hex[:8].upper()}"
            )

        super().save(*args, **kwargs)



    def __str__(self):

        return self.payment_reference



# ==========================================================
# LICENSE / ACTIVATION KEY SYSTEM
# ==========================================================

class LicenseKey(models.Model):

    subscription = models.OneToOneField(
        SchoolSubscription,
        on_delete=models.CASCADE,
        related_name="license",
    )


    key = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
    )


    activated = models.BooleanField(
        default=False,
    )


    activated_date = models.DateTimeField(
        null=True,
        blank=True,
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
    )


    def save(self, *args, **kwargs):

        if not self.key:

            self.key = (
                f"NXL-"
                f"{uuid.uuid4().hex[:12].upper()}"
            )

        super().save(*args, **kwargs)



    def activate(self):

        self.activated = True
        self.activated_date = timezone.now()
        self.save()


    def __str__(self):

        return self.key



# ==========================================================
# SCHOOL PROMOTION / MARKETING FEATURE
# ==========================================================

class SchoolPromotion(models.Model):

    PROMOTION_TYPES = (

        (
            "announcement",
            "Announcement",
        ),

        (
            "offer",
            "Special Offer",
        ),

        (
            "admission",
            "Admission Campaign",
        ),

    )


    title = models.CharField(
        max_length=150,
    )


    promotion_type = models.CharField(
        max_length=30,
        choices=PROMOTION_TYPES,
        default="announcement",
    )


    message = models.TextField()


    image = models.ImageField(
        upload_to="promotions/",
        blank=True,
        null=True,
    )


    start_date = models.DateField(
        default=timezone.now,
    )


    end_date = models.DateField()


    active = models.BooleanField(
        default=True,
    )


    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
    )



    def is_active(self):

        today = timezone.now().date()

        return (
            self.active
            and
            self.start_date <= today <= self.end_date
        )



    def __str__(self):

        return self.title



# ==========================================================
# DASHBOARD FINANCIAL HELPERS
# ==========================================================

class FinanceDashboard(models.Model):

    """
    Stores quick dashboard summaries.
    Used for admin dashboard cards.
    """

    updated_at = models.DateTimeField(
        auto_now=True,
    )


    def total_income_today(self):

        today = timezone.now().date()

        return Payment.objects.filter(
            payment_date__date=today
        ).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")



    def total_expenses_today(self):

        today = timezone.now().date()

        return Expense.objects.filter(
            expense_date=today
        ).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")



    def today_profit(self):

        return (
            self.total_income_today()
            -
            self.total_expenses_today()
        )



    def pending_fees(self):

        return Invoice.objects.filter(
            status__in=[
                "pending",
                "partial",
                "overdue",
            ]
        ).aggregate(
            total=Sum(
                models.F("amount_due")
                -
                models.F("amount_paid")
            )
        )["total"] or Decimal("0.00")



    def __str__(self):

        return "Finance Dashboard"