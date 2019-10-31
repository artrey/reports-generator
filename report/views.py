from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from report.forms import ReportForm


class SendReportView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('login')
    form_class = ReportForm
    template_name = 'report/send_report.html'

    def post(self, request, *args, **kwargs):
        redirect(reverse('report', args=(1,)))
