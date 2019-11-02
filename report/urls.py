from django.urls import path

from .views import SendReportView, pdf_report_view, reports_view, report_view

urls = [
    path('', SendReportView.as_view(), name='send_report'),
    path('reports/', reports_view, name='reports'),
    path('report/<int:rid>/', report_view, name='report'),
    path('report/<int:rid>/pdf/', pdf_report_view, name='pdf_report'),
]
