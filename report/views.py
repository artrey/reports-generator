from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, ListView

from report.forms import ReportForm
from report.models import Report, File, Task
from report.utils import build_report_pdf, build_task_pdf


def pdf_report_path(report: Report) -> str:
    return f'reports/{report.username}/' \
           f'ООП_Отчёт_{report.task.number}' \
           f'_{report.user.last_name}_{report.user.first_name}' \
           f'_{report.user.student_groups.first().title}.pdf'


@staff_member_required
def pdf_report_view(request, rid):
    report = get_object_or_404(Report, pk=rid)
    pdf_content = build_report_pdf(report, base_url=request.build_absolute_uri())
    return HttpResponse(pdf_content, content_type='application/pdf')


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
    pdf_content = build_task_pdf(task, base_url=request.build_absolute_uri())
    return HttpResponse(pdf_content, content_type='application/pdf')


class SendReportView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('login')
    form_class = ReportForm
    template_name = 'report/send_report.html'
    report_id = None

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('files')
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            self.report_id = report.id
            for f in files:
                File.objects.create(file=f, report=report)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('report', args=(self.report_id,))
