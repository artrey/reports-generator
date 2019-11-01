from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Group, Task, Report


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = 'title', 'link', 'users_count',

    def link(self, obj: Group) -> str:
        return mark_safe(
            f'<a href="{obj.upload_link}" target="_blank" rel="noopener noreferrer">{obj.upload_link}</a>'
        )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = 'number', 'title',
    list_display_links = 'title',


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = 'username', 'task', 'created_at', 'approved_at', 'rejected_at', 'comment',
    list_display_links = 'username',
    search_fields = 'user__last_name',
