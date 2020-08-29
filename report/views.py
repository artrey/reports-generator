from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from report.forms import ReportForm
from report.models import *
from report import tasks


@login_required
def pdf_report_view(request, rid):
    if request.user.is_staff:
        report = get_object_or_404(Report, pk=rid)
    else:
        report = get_object_or_404(Report, pk=rid, user=request.user)

    try:
        return HttpResponse(report.report_file.file, content_type='application/pdf')

    except Exception:
        raise Http404()


@login_required
def report_view(request, rid: int):
    report = get_object_or_404(Report, pk=rid, user=request.user)
    return render(request, 'report/report.html', context={
        'report': report,
    })


class TasksView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'report/tasks.html'


class ReportsView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'report/reports.html'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


@login_required
def pdf_task_view(request, tid: int):
    task = get_object_or_404(Task, pk=tid)

    try:
        return HttpResponse(task.task_file.file, content_type='application/pdf')

    except Exception:
        raise Http404()


class SendReportView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('login')
    form_class = ReportForm
    template_name = 'report/send_report.html'
    report_id = None

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('source_files')
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            self.report_id = report.id
            for f in files:
                SourceFile.objects.create(file=f, report=report)
            tasks.generate_report_pdf.delay(report.id)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('report', args=(self.report_id,))
