from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Invoice, Payment

@login_required
def parent_invoices(request):
    # Parent sees invoices for all children linked to their account
    from parentsApp.models import Parent
    parent = get_object_or_404(Parent, user=request.user)
    children = parent.parent_contact.all()  # related_name in Student model
    invoices = Invoice.objects.filter(student__in=children).select_related('fee_structure', 'student__user')
    context = {'invoices': invoices}
    return render(request, 'feesApp/parent_invoices.html', context)

@login_required
def student_invoices(request):
    # Student sees own invoices (if student logged in)
    from studentsApp.models import Student
    student = get_object_or_404(Student, user=request.user)
    invoices = Invoice.objects.filter(student=student)
    context = {'invoices': invoices}
    return render(request, 'feesApp/parent_invoices.html', context)

@login_required
def admin_invoice_report(request):
    if not request.user.is_staff:
        return redirect('home')
    invoices = Invoice.objects.select_related('student__user', 'fee_structure').all()
    total_collected = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    context = {'invoices': invoices, 'total_collected': total_collected}
    return render(request, 'feesApp/admin_report.html', context)