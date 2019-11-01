from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Group, File, Task, Report


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = 'title', 'link', 'users_count',

    def link(self, obj: Group) -> str:
        return mark_safe(
            f'<a href="{obj.upload_link}" target="_blank" rel="noopener noreferrer">{obj.upload_link}</a>'
        )
