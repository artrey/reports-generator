from django import forms

from report.models import Report


class ReportForm(forms.ModelForm):
    files = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'multiple': True}
    ))

    class Meta:
        model = Report
        fields = 'task', 'solution_text',
