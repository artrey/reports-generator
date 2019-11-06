from django.urls import path

from .views import SendReportView, TasksView, pdf_task_view, report_view, pdf_report_view

urls = [
    path('', SendReportView.as_view(), name='send_report'),
    path('tasks/', TasksView.as_view(), name='tasks'),
    path('task/<int:tid>/', pdf_task_view, name='task'),
    path('report/<int:rid>/', report_view, name='report'),
    path('report/<int:rid>/pdf/', pdf_report_view, name='pdf_report'),
]
