import os

from django import template

register = template.Library()


@register.filter
def humanize_status(raw: str) -> str:
    if raw == 'approved':
        return 'Принят'
    elif raw == 'rejected':
        return 'Отклонён'
    elif raw == 'verifying':
        return 'На проверке'
    return 'Неопределённое состояние'


@register.filter
def file_content(file) -> str:
    try:
        return file.read().decode(errors='ignore')
    except IOError:
        return ''


@register.filter
def basename(file) -> str:
    return os.path.basename(file)


@register.filter
def status2color(status: str) -> str:
    if status == 'approved':
        return 'lightgreen'
    elif status == 'rejected':
        return 'lightpink'
    return 'white'
