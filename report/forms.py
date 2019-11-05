from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms

from report.models import Report, Task


class TaskAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Task
        fields = '__all__'


class ReportAdminForm(forms.ModelForm):
    solution_text = forms.CharField(widget=CKEditorUploadingWidget())
    comment = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Report
        fields = '__all__'


class ReportForm(forms.ModelForm):
    solution_text = forms.CharField(widget=CKEditorUploadingWidget())
    files = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'multiple': True}
    ))

    class Meta:
        model = Report
        fields = 'task', 'solution_text', 'files',
