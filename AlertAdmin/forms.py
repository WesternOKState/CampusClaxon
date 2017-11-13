from django import forms
from .models import SUBSCRIBER_STATUS_CHOICES, TOPIC_TYPE_CHOICES, AUTH_CHOICES, SMS_PROVIDER_CHOICES
from django.contrib.auth.models import User
from .models import Topic, Setting

# def topic_choices():
#     choices = []
#     topics = Topic.objects.all()
#     for topic in topics:
#         choices.append((topic.id, topic.topic_name))
#     return choices

class MyMessageForm(forms.Form):
    template = forms.CharField(widget=forms.Select(attrs={'class':'form-control'}), required=False)
    topic = forms.CharField(widget=forms.Select(attrs={'class':'form-control'}), required=False)
    message = forms.CharField(max_length = 140, widget=forms.Textarea(
        attrs={'class':'form-control','maxlength':'140'}))

    def sendMessage(self):
        pass

class SettingsForm(forms.Form):
    security_key = forms.CharField(widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'50'}))
    secret_key = forms.CharField(widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'150'}))
    theme_name = forms.CharField(widget=forms.Select(
        attrs={'class':'form-control','maxlength':'50'}))
    authentication_type = forms.CharField(widget=forms.Select(choices=AUTH_CHOICES,
        attrs={'class': 'form-control', 'maxlength': '50'}))
    quick_alert_auth_code = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'maxlength': '100'}))
    globaltopic = forms.ModelChoiceField(queryset=Topic.objects.filter(topic_type='required'), widget=forms.Select(
        attrs={'class': 'form-control', 'maxlength': '50'}))
    sms_provider = forms.CharField(widget=forms.Select(choices=SMS_PROVIDER_CHOICES,
        attrs={'class': 'form-control', 'maxlength': '100'}))

class TemplateForm(forms.Form):
    topic_name = forms.CharField(widget=forms.Select(
        attrs={'class': 'form-control'}))

    # topic = forms.CharField(widget=forms.Select(choices=topic_choices(),
    #     attrs={'class': 'form-control'}))
    template_name = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'30'}))
    default_message = forms.CharField(max_length=160, widget=forms.Textarea(
        attrs={'class':'form-control','maxlength':'160'}))


# class TopicForm(forms.Form):
#     topic_name = forms.CharField(max_length=100, widget=forms.TextInput(
#         attrs={'class':'form-control','maxlength':'100'}))
#     display_name = forms.CharField(max_length=100, widget=forms.TextInput(
#         attrs={'class':'form-control','maxlength':'100'}))
#     topic_owner = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.Select(
#         attrs={'class': 'form-control'}))


class NewTopicForm(forms.Form):
    topic_name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'100'}))
    display_name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'100'}))
    topic_owner = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.Select(
        attrs={'class': 'form-control'}))
    type = forms.CharField(widget=forms.Select(
        attrs={'class': 'form-control'}, choices=TOPIC_TYPE_CHOICES))
    description = forms.CharField(max_length=100, widget=forms.Textarea(
        attrs={'class':'form-control','maxlength':'1024'}))


class EditCellPhone(forms.Form):
    old_number = forms.CharField(max_length=100, widget=forms.HiddenInput(
        attrs={'class':'form-control','maxlength':'100'}))
    new_number = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'100'}))

class SubscriberForm(forms.Form):
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'30'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'30'}))
    student_id = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'30'}))
    personal_email = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'50'}))
    school_email = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'50'}))
    opt_out = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class':'form-control'}))
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(
        attrs={'class':'form-control','maxlength':'50'}), required=False)

class AddSubscriberForm(forms.Form):
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'30'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'30'}))
    cell_phone = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'30'}))
    student_id = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'30'}))
    personal_email = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'50'}))
    school_email = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'50'}))
    opt_out = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(
        attrs={'class':'form-control','maxlength':'50'}), required=False)


class FileUploadForm(forms.Form):
    import_file = forms.FileField()

class QuickAlertForm(forms.Form):
    template = forms.CharField(widget=forms.Select(attrs={'class':'form-control'}), required=False)
    message = forms.CharField(max_length = 140, widget=forms.Textarea(
        attrs={'class':'form-control','maxlength':'140'}))
    auth_code = forms.CharField(max_length=100, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'maxlength': '100'}), required=True)


    def clean(self):
        print("################################")
        my_settings = Setting.objects.all()[0]
        cleaned_data = super(QuickAlertForm, self).clean()
        cc_auth_code = cleaned_data.get('auth_code')
        if my_settings.quick_alert_auth_code != cc_auth_code:
                self.add_error('auth_code', "Please enter the correct authorization code.")


class QuickSevereWeatherForm(forms.Form):
    template = forms.CharField(widget=forms.Select(attrs={'class':'form-control'}), required=False)
    close_time = forms.CharField(max_length = 140, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'140'}))
    auth_code = forms.CharField(max_length=100, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'maxlength': '100'}), required=True)


    def clean(self):
        print("################################")
        my_settings = Setting.objects.all()[0]
        cleaned_data = super(QuickSevereWeatherForm, self).clean()
        cc_auth_code = cleaned_data.get('auth_code')
        if my_settings.quick_alert_auth_code != cc_auth_code:
                self.add_error('auth_code', "Please enter the correct authorization code.")


class QuickSchoolClosingForm(forms.Form):
    template = forms.CharField(widget=forms.Select(attrs={'class':'form-control'}), required=False)
    close_time = forms.CharField(max_length = 140, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'140'}))
    reason =  forms.CharField(max_length = 140, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'140'}))
    auth_code = forms.CharField(max_length=100, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'maxlength': '100'}), required=True)


    def clean(self):
        print("################################")
        my_settings = Setting.objects.all()[0]
        cleaned_data = super(QuickSchoolClosingForm, self).clean()
        cc_auth_code = cleaned_data.get('auth_code')
        if my_settings.quick_alert_auth_code != cc_auth_code:
                self.add_error('auth_code', "Please enter the correct authorization code.")

class QuickOutageForm(forms.Form):
    template = forms.CharField(widget=forms.Select(attrs={'class':'form-control'}), required=False)
    auth_code = forms.CharField(max_length=100, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'maxlength': '100'}), required=True)


    def clean(self):
        print("################################")
        my_settings = Setting.objects.all()[0]
        cleaned_data = super(QuickOutageForm, self).clean()
        cc_auth_code = cleaned_data.get('auth_code')
        if my_settings.quick_alert_auth_code != cc_auth_code:
                self.add_error('auth_code', "Please enter the correct authorization code.")

class QuickOnlineDowntimeForm(forms.Form):
    template = forms.CharField(widget=forms.Select(attrs={'class':'form-control'}), required=False)
    close_time = forms.CharField(max_length = 140, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'140'}))
    reason =  forms.CharField(max_length = 140, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'140'}))
    auth_code = forms.CharField(max_length=100, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'maxlength': '100'}), required=True)


    def clean(self):
        print("################################")
        my_settings = Setting.objects.all()[0]
        cleaned_data = super(QuickOnlineDowntimeForm, self).clean()
        cc_auth_code = cleaned_data.get('auth_code')
        if my_settings.quick_alert_auth_code != cc_auth_code:
                self.add_error('auth_code', "Please enter the correct authorization code.")