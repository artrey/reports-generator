import os

from django import template

register = template.Library()


@register.filter
def humanize_status(raw: str) -> str:
    if raw == 'approved':
        return 'Принятые'
    elif raw == 'rejected':
        return 'Отклонённые'
    elif raw == 'verifying':
        return 'На проверке'
    return 'Все'


@register.filter
def file_content(file) -> str:
    try:
        return file.read().decode()
    except IOError:
        return ''


@register.filter
def basename(file) -> str:
    return os.path.basename(file)
