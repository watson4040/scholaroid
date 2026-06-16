from django.shortcuts import render, redirect
from .forms import EnrollmentForm

def enrollment_request(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('enrollment_success')
    else:
        form = EnrollmentForm()
    return render(request, 'studentsApp/enrollment_form.html', {'form': form})

def enrollment_success(request):
    return render(request, 'studentsApp/enrollment_success.html')