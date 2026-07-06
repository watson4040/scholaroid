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

# ─── Admin Views ───
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
        messages.success(self.request, "Exam created.")
        return super().form_valid(form)

class AdminExamUpdate(AdminRequiredMixin, UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = 'examsApp/admin_exam_form.html'
    success_url = reverse_lazy('admin_exams_list')

    def form_valid(self, form):
        messages.success(self.request, "Exam updated.")
        return super().form_valid(form)

class AdminExamDelete(AdminRequiredMixin, DeleteView):
    model = Exam
    template_name = 'examsApp/admin_exam_confirm_delete.html'
    success_url = reverse_lazy('admin_exams_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Exam deleted.")
        return super().delete(request, *args, **kwargs)

# ─── Teacher Views ───
class TeacherExamList(ListView):
    model = Exam
    template_name = 'examsApp/teacher_exam_list.html'
    paginate_by = 15
    ordering = ['exam_date']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'teacher'):
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        teacher = self.request.user.teacher
        # CORRECTED: use assigned_class (ManyToManyField)
        classes = teacher.assigned_class.all()
        return Exam.objects.filter(class_room__in=classes).select_related('subject', 'class_room').order_by('exam_date')


class TeacherExamCreate(CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'examsApp/teacher_exam_form.html'
    success_url = reverse_lazy('teacher_exams_list')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'teacher'):
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the teacher to the form to filter choices
        kwargs['teacher'] = self.request.user.teacher
        return kwargs

    def form_valid(self, form):
        teacher = self.request.user.teacher
        class_room = form.cleaned_data.get('class_room')
        subject = form.cleaned_data.get('subject')
        # Validate that class and subject belong to teacher
        if class_room not in teacher.assigned_class.all():
            messages.error(self.request, "You are not assigned to this class.")
            return redirect('teacher_exams_list')
        if subject not in teacher.subject.all():
            messages.error(self.request, "You are not assigned to this subject.")
            return redirect('teacher_exams_list')
        response = super().form_valid(form)
        messages.success(self.request, "Exam created successfully.")
        return response