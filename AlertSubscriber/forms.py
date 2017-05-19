from django import forms



class SubscriberForm(forms.Form):
    personal_email = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'50'}))
    opt_out = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class':'form-control'}))
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(
        attrs={'class':'form-control','maxlength':'50'}), required=False)


class EditCellPhone(forms.Form):
    old_number = forms.CharField(max_length=100, widget=forms.HiddenInput(
        attrs={'class':'form-control','maxlength':'100'}))
    new_number = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'100'}))

class MyMessageForm(forms.Form):
    topic = forms.CharField(widget=forms.Select(attrs={'class':'form-control'}), required=False)
    message = forms.CharField(max_length = 140, widget=forms.Textarea(
        attrs={'class':'form-control','maxlength':'140'}))