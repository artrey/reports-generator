from django.urls import path

from .views import (
    SendReportView, TasksView, ReportsView,
    pdf_task_view, report_view, pdf_report_view, reports_comparator_view,
)

urls = [
    path('', SendReportView.as_view(), name='send_report'),
    path('reports/', ReportsView.as_view(), name='reports'),
    path('tasks/', TasksView.as_view(), name='tasks'),
    path('task/<int:tid>/', pdf_task_view, name='task'),
    path('report/<int:rid>/', report_view, name='report'),
    path('report/<int:rid>/pdf/', pdf_report_view, name='pdf_report'),
    path('report/comparator/<int:tid>/', reports_comparator_view, name='reports_comparator'),
]
