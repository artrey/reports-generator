from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from weasyprint import HTML, CSS

from report.forms import ReportForm
from report.models import Report, File


raw_html = """<h2>gruohtrht rtgb rgh ruifbhirdtfbv hidtbghr</h2><h2>tbgih rtbgih tgij htbgivh itghd birghd bihg br</h2>
<code class="php hljs">dfhfd
s gdfgsdf\n
s dfg\n
s df\n
h d\r\n
fg j<br/>
tfy
jyujkgyjkguj f
dg
</code>"""
raw_css = """@media print {h2 {page-break-before: always;} .php{border: solid black 1px}}"""


@staff_member_required
def pdf_report_view(request, rid):
    HTML(string=raw_html).render(stylesheets=[CSS(string=raw_css)]).write_pdf('test.pdf')
    report = get_object_or_404(Report, pk=rid)
    for f in report.files.all():
        print(f)
    # TODO: gen report
    return HttpResponse(str(report))


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
