from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms

from report.models import Report, Task


class TaskAdminForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            'description': CKEditorUploadingWidget(),
        }


class ReportAdminForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = '__all__'
        widgets = {
            'solution_text': CKEditorUploadingWidget(),
            'comment': CKEditorUploadingWidget(),
        }


class ReportForm(forms.ModelForm):
    source_files = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'multiple': True}
    ))
    task = forms.ModelChoiceField(queryset=Task.get_enabled())

    class Meta:
        model = Report
        fields = 'task', 'solution_text', 'source_files',
        widgets = {
            'solution_text': CKEditorUploadingWidget(),
        }
