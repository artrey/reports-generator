import os

from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.core.exceptions import ValidationError

from report import utils
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

    def clean_source_files(self):
        for file in self.files.getlist('source_files'):
            if not utils.is_valid_filename_ext(os.path.splitext(file.name)[-1]):
                raise ValidationError(
                    'Попытка загрузить неподдерживаемый файл. '
                    'Загрузите файлы с исходным кодом: .cpp, .cs, .java и т.п.'
                )
        return self.cleaned_data['source_files']

    class Meta:
        model = Report
        fields = 'task', 'solution_text', 'source_files',
        widgets = {
            'solution_text': CKEditorUploadingWidget(),
        }
