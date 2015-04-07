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


class DollarsDashboardForm(forms.Form):
    tester_pass_slot = forms.DecimalField(max_digits=12, required=True,
                                          widget=forms.TextInput(attrs={'class': 'form-control input-sm'}))
    tester_fail_slot = forms.DecimalField(max_digits=12, required=True,
                                          widget=forms.TextInput(attrs={'class': 'form-control input-sm'}))
    tester_new_slot = forms.DecimalField(max_digits=12, required=True,
                                         widget=forms.TextInput(attrs={'class': 'form-control input-sm'}))
    auto_new_slot = forms.DecimalField(max_digits=12, required=True,
                                       widget=forms.TextInput(attrs={'class': 'form-control input-sm'}))
    auto_pass_slot = forms.DecimalField(max_digits=12, required=True,
                                        widget=forms.TextInput(attrs={'class': 'form-control input-sm'}))
    auto_fail_slot = forms.DecimalField(max_digits=12, required=True,
                                        widget=forms.TextInput(attrs={'class': 'form-control input-sm'}))
    auto_missing_slot = forms.DecimalField(max_digits=12, required=True,
                                           widget=forms.TextInput(attrs={'class': 'form-control input-sm'}))
    update_file_status = forms.DecimalField(max_digits=12, required=True,
                                            widget=forms.TextInput(attrs={'class': 'form-control input-sm'}))
    elasticsearch_url = forms.CharField(max_length=100, required=True,
                                        widget=forms.TextInput(attrs={'class': 'form-control input-sm'}))
    elasticsearch_index = forms.CharField(max_length=40, required=True,
                                          widget=forms.TextInput(attrs={'class': 'form-control input-sm'}))
