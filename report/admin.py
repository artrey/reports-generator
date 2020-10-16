import typing
from urllib.parse import urlencode

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


class ReportsSimilarityInline(admin.TabularInline):
    model = ReportsSimilarity
    fk_name = 'left'
    readonly_fields = 'right', 'ratio', 'compare',
    extra = 0
    can_delete = False

    def compare(self, obj: ReportsSimilarity) -> str:
        return make_link(
            reverse('reports_comparator', args=(obj.left.task_id,)) + '?' + urlencode({
                'src': obj.left.id,
                'dst': obj.right.id,
            }), 'Compare'
        )


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
    inlines = ReportsSimilarityInline, SourceFileInline,

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
                group = obj.user.student_groups.first()
                if not group:
                    raise RuntimeError(f'User "{obj.user.get_full_name()}" '
                                       'is not associated with any group')
                google_folder_name = f'{group.title}-Lab{obj.task.number:02}'

                folder = GoogleApiFolder.objects.filter(title=google_folder_name).first()
                if not folder:
                    raise RuntimeError("GoogleApiFolder not found: report wasn't uploaded to Google Drive")

                file_id = gapi.upload_file(folder.api_id, build_report_name(obj), pdf_content)
                gapi.update_results(
                    settings.GAPI_RESULT_SHEET, obj, gapi.build_file_link(file_id), '_approve' in request.POST
                )

            except Exception as ex:
                messages.add_message(request, messages.WARNING, ex)

        elif '_reject' in request.POST:
            obj.approved_at = None
            obj.rejected_at = timezone.now()
            obj.save()

        return super().response_change(request, obj)
