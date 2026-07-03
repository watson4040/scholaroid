from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404
from accountsApp.mixins import AdminRequiredMixin
from .models import Exam
from .forms import ExamForm
from teachersApp.models import Teacher
from classesApp.models import ClassRoom, Subjects

class AdminExamList(AdminRequiredMixin, ListView):
    model = Exam
    template_name = 'examsApp/admin_exam_list.html'
    paginate_by = 15
    ordering = ['exam_date']

class AdminExamCreate(AdminRequiredMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'examsApp/admin_exam_form.html'
    success_url = reverse_lazy('admin_exams_list')

    def form_valid(self, form):
        messages.success(self, "Exam created.")
        return super().form_valid(form)

class AdminExamUpdate(AdminRequiredMixin, UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = 'examsApp/admin_exam_form.html'
    success_url = reverse_lazy('admin_exams_list')

    def form_valid(self, form):
        messages.success(self, "Exam updated.")
        return super().form_valid(form)

class AdminExamDelete(AdminRequiredMixin, DeleteView):
    model = Exam
    template_name = 'examsApp/admin_exam_confirm_delete.html'
    success_url = reverse_lazy('admin_exams_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self, "Exam deleted.")
        return super().delete(request, *args, **kwargs)

class TeacherExamList(ListView):
    model = Exam
    template_name = 'examsApp/teacher_exam_list.html'
    paginate_by = 15
    ordering = ['exam_date']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'teacher'):
            return redirect('dashboard_teacher') if request.user.role == 'teacher' else redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        teacher = self.request.user.teacher
        classes = teacher.assigned_class.all()
        return Exam.objects.filter(class_room__in=classes).select_related('subject', 'class_room').order_by('exam_date')

# ─── NEW: Teacher exam creation ───
class TeacherExamCreate(CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'examsApp/teacher_exam_form.html'
    success_url = reverse_lazy('teacher_exam_list')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'teacher'):
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Optionally pass the teacher to the form to filter subjects/classes
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher
        context['teacher'] = teacher
        # Get classes assigned to this teacher
        context['classes'] = teacher.assigned_class.all() if hasattr(teacher, 'assigned_class') else []
        # Get subjects assigned to this teacher (assuming ManyToManyField on Teacher model)
        context['subjects'] = teacher.subject.all() if hasattr(teacher, 'subject') else []
        return context

    def form_valid(self, form):
        # Ensure the class and subject belong to the teacher
        teacher = self.request.user.teacher
        class_id = form.cleaned_data.get('class_room').id
        subject_id = form.cleaned_data.get('subject').id
        # Check if teacher is assigned to that class and subject
        if class_id not in [c.id for c in teacher.assigned_class.all()]:
            messages.error(self.request, "You are not assigned to this class.")
            return redirect('teacher_exam_list')
        if subject_id not in [s.id for s in teacher.subject.all()]:
            messages.error(self.request, "You are not assigned to this subject.")
            return redirect('teacher_exam_list')
        # Save the exam
        response = super().form_valid(form)
        messages.success(self.request, "Exam created successfully.")
        return response