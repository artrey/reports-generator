from os import makedirs
from os.path import dirname

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from weasyprint import HTML

from report.forms import ReportForm
from report.models import Report, File


def pdf_report_path(report: Report) -> str:
    return f'reports/{report.username}/' \
           f'ООП_Отчёт_{report.task.number}' \
           f'_{report.user.last_name}_{report.user.first_name}' \
           f'_{report.user.student_groups.first().title}.pdf'


@staff_member_required
def pdf_report_view(request, rid):
    report = get_object_or_404(Report, pk=rid)
    pdf_filename = pdf_report_path(report)
    makedirs(dirname(pdf_filename), exist_ok=True)
    HTML(string=render_to_string('report/pdf_report_template.html', context={
        'files': map(lambda x: print(x), report.files.all())
    })).render().write_pdf(pdf_filename)
    return FileResponse(open(pdf_filename, 'rb'))


def reports_view(request):
    status = request.GET.get('status')
    reports = Report.statuses().get(status, Report.objects).filter(user=request.user)
    return render(request, 'report/reports.html', context={
        'status': status,
        'reports': reports,
    })


@login_required
def report_view(request, rid: int):
    report = get_object_or_404(Report, pk=rid, user=request.user)
    return render(request, 'report/report.html', context={
        'report': report,
    })


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
