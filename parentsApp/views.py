import logging
from django.shortcuts import render, redirect
from studentsApp.models import Student
from accountsApp.models import Notice
from django.contrib.auth.decorators import login_required
from attendanceApp.models import Attendance
from django.utils.timezone import now
from django.contrib import messages
from .forms import LinkChildForm
from teachersApp.models import PupilReport

logger = logging.getLogger(__name__)

@login_required
def dashboard_parent(request):
    parent = request.user.parent
    children = Student.objects.filter(parent=parent)
    notices = Notice.objects.order_by('-created_at')[:5]
    today = now().date()
    attendance_records = Attendance.objects.filter(student__in=children, date=today)
    attendance_map = {rec.student.id: rec.status for rec in attendance_records}

    # attendance percentage
    total_present = 0
    total_marked = 0
    for child in children:
        child_att = Attendance.objects.filter(student=child)
        child_total = child_att.count()
        if child_total:
            child_present = child_att.filter(status='present').count()
            total_present += (child_present / child_total) * 100
            total_marked += 1
    avg_attendance_pct = round(total_present / total_marked, 1) if total_marked else 0

    # ----- REPORTS -----
    reports = PupilReport.objects.filter(
        pupil__in=children,
        is_submitted=True
    ).select_related('pupil', 'teacher', 'teacher__user').order_by('-updated_at')

    # 🔍 Debug logging
    child_ids = [child.id for child in children]
    logger.info(f"Parent {parent.user.id} has children: {child_ids}")
    logger.info(f"Found {reports.count()} submitted reports for these children.")

    stats = {
        'children': children.count(),
        'avg_attendance_pct': avg_attendance_pct,
        'notices': notices.count(),
    }

    context = {
        "parent": parent,
        "children": children,
        "notices": notices,
        "attendance_map": attendance_map,
        "stats": stats,
        "reports": reports,
        "reports_count": reports.count(),  # <-- added for template
    }
    return render(request, "parentsApp/dashboard.html", context)

# Link child view remains unchanged
@login_required
def link_child(request):
    parent = request.user.parent
    if request.method == 'POST':
        form = LinkChildForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            try:
                student = Student.objects.get(user__email__iexact=email)
            except Student.DoesNotExist:
                form.add_error('email', 'This email is not registered as a student.')
            else:
                if getattr(student.user, 'role', '') != 'student':
                    form.add_error('email', 'This account is not registered with a student role.')
                elif student.parent and student.parent != parent:
                    form.add_error('email', 'This student is already linked to another parent.')
                elif student.parent == parent:
                    messages.info(request, 'This student is already linked to your account.')
                    return redirect('dashboard_parent')
                else:
                    student.parent = parent
                    student.save()
                    messages.success(request, f"Successfully linked {student.user.get_full_name() or student.user.username}.")
                    return redirect('dashboard_parent')
    else:
        form = LinkChildForm()
    return render(request, 'parentsApp/link_child.html', {'form': form})