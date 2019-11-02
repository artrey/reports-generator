from django.urls import path

from .views import SendReportView, pdf_report

urls = [
    path('', SendReportView.as_view(), name='send_report'),
    path('reports/', SendReportView.as_view(), name='reports'),
    path('report/<int:rid>/', SendReportView.as_view(), name='report'),
    path('report/<int:rid>/pdf/', pdf_report, name='pdf_report'),
]
