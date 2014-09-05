from django import forms


class ProjectForm(forms.Form):
    name = forms.CharField(max_length=50, required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name'}))
    file = forms.FileField(max_length=100, required=False)


class UploadForm(forms.Form):
    file = forms.FileField(max_length=100, required=True)