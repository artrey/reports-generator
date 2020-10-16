from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from report.forms import ReportForm
from report.models import *
from report import tasks, utils


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
    queryset = Task.get_enabled()
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
            tasks.check_uniqueness.delay(report.id)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('report', args=(self.report_id,))


@staff_member_required
def reports_comparator_view(request, tid: int):
    report_src_id = request.GET.get('src')
    report_dst_id = request.GET.get('dst')

    report_src = get_object_or_404(Report, pk=report_src_id, task_id=tid)
    report_dst = get_object_or_404(Report, pk=report_dst_id, task_id=tid)

    ratio = utils.ratio_reports(report_src, report_dst)
    results = utils.compare_reports(report_src, report_dst)

    return render(request, 'report/comparator.html', context={
        'task': get_object_or_404(Task, pk=tid),
        'reports': Report.objects.filter(task_id=tid),
        'report_src_id': report_src.id,
        'report_dst_id': report_dst.id,
        'results': results,
        'ratio': ratio,
    })
