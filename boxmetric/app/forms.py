from django import forms

class SignupForm(forms.Form):
    gmail = forms.EmailField(widget=forms.TextInput(), error_messages={'required': 'Please enter a valid email:'})
    invitation = forms.CharField(max_length=6, widget=forms.TextInput(), required=False)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), error_messages={'required': 'Please enter a password:'})
