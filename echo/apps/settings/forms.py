from django import forms
from models import PreprodServer


class ServerForm(forms.Form):
    name = forms.CharField(max_length=50, required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control input-sm', 'placeholder': 'Server Name'}))
    address = forms.CharField(max_length=50, required=True,
                              widget=forms.TextInput(attrs={'class': 'form-control input-sm', 'placeholder': 'Server Address'}))
    account = forms.CharField(max_length=50, required=True,
                              widget=forms.TextInput(attrs={'class': 'form-control input-sm', 'placeholder': 'Service Account'}))


class ServerPreprodForm(forms.Form):
    name = forms.CharField(max_length=50, required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control input-sm', 'placeholder': 'Server Name'}))
    address = forms.CharField(max_length=50, required=True,
                              widget=forms.TextInput(attrs={'class': 'form-control input-sm', 'placeholder': 'Server Address'}))
    account = forms.CharField(max_length=50, required=True,
                              widget=forms.TextInput(attrs={'class': 'form-control input-sm', 'placeholder': 'Service Account'}))
    application_type = forms.ChoiceField(widget=forms.RadioSelect,
                                         choices=PreprodServer.APPLICATION_TYPE_CHOICES)

