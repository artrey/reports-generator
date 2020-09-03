import typing

from django.conf import settings
from django.contrib import admin, messages
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from .forms import TaskAdminForm, ReportAdminForm
from . import gapi
from .utils import build_report_pdf
from .models import *


def make_link(href: str, title: str = None) -> str:
    title = title or href
    return mark_safe(
        f'<a href="{href}" target="_blank" rel="noopener noreferrer">{title}</a>'
    )


def build_report_name(report: Report) -> str:
    return f'ООП_Отчёт_{report.task.number}' \
           f'_{report.user.last_name}_{report.user.first_name}' \
           f'_{report.user.student_groups.first().title}.pdf'


@admin.register(GoogleApiFolder)
class GoogleApiFolderAdmin(admin.ModelAdmin):
    list_display = 'title', 'api_id', 'link',

    def link(self, obj: GoogleApiFolder) -> str:
        return make_link(gapi.build_folder_link(obj.api_id), 'Open')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = 'title', 'link', 'users_count',
    filter_horizontal = 'users',

    def link(self, obj: Group) -> typing.Optional[str]:
        if obj.folder:
            return make_link(gapi.build_folder_link(obj.folder.api_id))
        return None


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskAdminForm
    list_display = 'number', 'title', 'preview', 'enabled',
    list_display_links = 'title',

    def preview(self, obj: Report) -> str:
        return make_link(reverse('task', args=(obj.id,)), 'Open')


@admin.register(ReportsFolder)
class ReportsFolderAdmin(admin.ModelAdmin):
    list_display = 'folder', 'group', 'task', 'link',
    list_filter = 'group', 'task',
    search_fields = 'group__title', 'task__title', 'folder__title',

    def link(self, obj: ReportsFolder) -> str:
        return make_link(gapi.build_folder_link(obj.folder.api_id))


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
        filter_func = Report.filtered_queryset().get(self.value())
        if filter_func:
            queryset = filter_func(queryset)
        return queryset


class SourceFileInline(admin.TabularInline):
    model = SourceFile
    extra = 0


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
    inlines = SourceFileInline,

    def first_group(self, obj: Report) -> Group:
        return obj.user.student_groups.first()
    first_group.short_description = 'group'

    def preview(self, obj: Report) -> str:
        return make_link(reverse('pdf_report', args=(obj.id,)), 'Report')

    def response_change(self, request, obj: Report):
        if '_approve' in request.POST or '_approve_without_score' in request.POST:
            obj.approved_at = timezone.now()
            obj.rejected_at = None
            obj.save()

            try:
                pdf_content = obj.report_file.file.read()
                folder = ReportsFolder.objects.filter(task=obj.task, group=obj.user.student_groups.first()).first()
                if folder:
                    file_id = gapi.upload_file(folder.folder.api_id, build_report_name(obj), pdf_content)
                    gapi.update_results(
                        settings.GAPI_RESULT_SHEET, obj, gapi.build_file_link(file_id), '_approve' in request.POST
                    )
                else:
                    messages.add_message(request, messages.WARNING,
                                         "Report wasn't upload to Google Drive. Reason: ReportsFolder not found")

            except StopIteration:
                messages.add_message(request, messages.ERROR, f'Error: user or task not found in google sheet')

            except Exception as ex:
                messages.add_message(request, messages.ERROR, f'Some error occurred. Info: {ex}')

        elif '_reject' in request.POST:
            obj.approved_at = None
            obj.rejected_at = timezone.now()
            obj.save()

        return super().response_change(request, obj)
