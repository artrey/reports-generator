from django.template.loader import render_to_string
from weasyprint import HTML

from report.models import Report, Task


def build_pdf(html: str, **kwargs):
    return HTML(string=html, **kwargs).render().write_pdf()


def build_pdf_by_template(template: str, context: dict, **kwargs):
    return build_pdf(render_to_string(template, context=context), **kwargs)


def build_report_pdf(report: Report, **kwargs):
    return build_pdf_by_template('report/pdf_report_template.html', {'report': report}, **kwargs)


def build_task_pdf(task: Task, **kwargs):
    return build_pdf_by_template('report/pdf_task_template.html', {'task': task}, **kwargs)
