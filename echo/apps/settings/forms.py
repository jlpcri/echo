from django import forms


class ServerForm(forms.Form):
    name = forms.CharField(max_length=50, required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control input-sm', 'placeholder': 'Server Name'}))
    address = forms.CharField(max_length=50, required=True,
                              widget=forms.TextInput(attrs={'class': 'form-control input-sm', 'placeholder': 'Server Address'}))
    account = forms.CharField(max_length=50, required=True,
                              widget=forms.TextInput(attrs={'class': 'form-control input-sm', 'placeholder': 'Service Account'}))