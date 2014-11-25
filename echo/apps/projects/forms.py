from django import forms
from echo.apps.settings.models import Server


class ProjectForm(forms.Form):
    name = forms.CharField(max_length=50, required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name'}))
    root_path = forms.CharField(max_length=50, required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bravo Server Path'}))
    file = forms.FileField(max_length=100, required=False)


class UploadForm(forms.Form):
    file = forms.FileField(max_length=100, required=True)


class ServerForm(forms.Form):
    server = forms.ModelChoiceField(required=False, queryset=Server.objects.all(),
                               widget=forms.Select(attrs={'class': 'form-control'}))


class ProjectRootPathForm(forms.Form):
    root_path = forms.CharField(max_length=50, required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bravo Server Path'}))