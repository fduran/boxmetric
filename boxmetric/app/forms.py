from django import forms

class GmailField(forms.EmailField):
    def clean(self, data):
        super(GmailField, self).clean(data)
        if str(data.split('@')[1]).lower() != 'gmail.com':
            raise forms.ValidationError('This is not a valid Gmail address.')
        return data


class SignupForm(forms.Form):
    gmail = GmailField(widget=forms.TextInput(), error_messages={'required': 'Enter an e-mail address:'})
    invitation = forms.CharField(max_length=6, widget=forms.TextInput(), required=False)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), error_messages={'required': 'Enter a password:'})


