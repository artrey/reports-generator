from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from report.forms import TaskAdminForm, ReportAdminForm
from .models import Group, Task, Report


def make_link(href: str, title: str = None) -> str:
    title = title or href
    return mark_safe(
        f'<a href="{href}" target="_blank" rel="noopener noreferrer">{title}</a>'
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = 'title', 'link', 'users_count',

    def link(self, obj: Group) -> str:
        return make_link(obj.upload_link)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskAdminForm
    list_display = 'number', 'title',
    list_display_links = 'title',


class FirstGroupFilter(admin.SimpleListFilter):
    title = 'group'
    parameter_name = 'group'

    def lookups(self, request, model_admin):
        return ((g.title, g.title) for g in Group.objects.only('title').all())

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(user__student_groups__title=value)


class StatusReportFilter(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return ((x, x) for x in Report.statuses().keys())

    def queryset(self, request, queryset):
        q = Report.statuses().get(self.value())
        if q:
            queryset = q.all()
        return queryset


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    form = ReportAdminForm
    change_form_template = 'report/report_admin_form.html'

    list_display = (
        'username', 'first_group', 'task', 'created_at',
        'approved_at', 'rejected_at', 'comment', 'preview',
    )
    list_display_links = 'username',
    search_fields = 'user__last_name', 'user__first_name', 'task__title',
    list_filter = 'task', FirstGroupFilter, StatusReportFilter,
    readonly_fields = 'created_at',
    save_on_top = True

    def first_group(self, obj: Report) -> Group:
        return obj.user.student_groups.first()
    first_group.short_description = 'group'

    def preview(self, obj: Report) -> str:
        return make_link(reverse('pdf_report', args=(obj.id,)), 'Отчёт')

    def response_change(self, request, obj: Report):
        if "_approve" in request.POST:
            obj.approved_at = timezone.now()
            obj.rejected_at = None
            obj.save()
            # TODO: generate report + send to gdrive
        elif "_reject" in request.POST:
            obj.approved_at = None
            obj.rejected_at = timezone.now()
            obj.save()
        return super().response_change(request, obj)
