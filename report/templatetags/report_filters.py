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
