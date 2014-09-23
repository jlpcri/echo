from django import forms
from echo.apps.settings.models import Server


class ProjectForm(forms.Form):
    name = forms.CharField(max_length=50, required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name'}))
    file = forms.FileField(max_length=100, required=False)


class UploadForm(forms.Form):
    file = forms.FileField(max_length=100, required=True)


class ServerForm(forms.Form):
    server = forms.ChoiceField(required=True, choices=Server.choices(),
                               widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(ServerForm, self).__init__(*args, **kwargs)
        self.choices = Server.choices()