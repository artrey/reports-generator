from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from report.forms import ReportForm
from report.models import Report


@staff_member_required
def pdf_report(request, rid):
    report = get_object_or_404(Report, pk=rid)
    # TODO: gen report
    return HttpResponse(str(report))


class SendReportView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('login')
    form_class = ReportForm
    template_name = 'report/send_report.html'

    def post(self, request, *args, **kwargs):
        redirect(reverse('report', args=(1,)))
