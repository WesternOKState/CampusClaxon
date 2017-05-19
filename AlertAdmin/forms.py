from django import forms
from .models import SUBSCRIBER_STATUS_CHOICES, TOPIC_TYPE_CHOICES, AUTH_CHOICES
from django.contrib.auth.models import User
from .models import Topic

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
    aws_security_key = forms.CharField(widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'50'}))
    aws_secret_key = forms.CharField(widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'150'}))
    theme_name = forms.CharField(widget=forms.Select(
        attrs={'class':'form-control','maxlength':'50'}))
    authentication_type = forms.CharField(widget=forms.Select(choices=AUTH_CHOICES,
        attrs={'class': 'form-control', 'maxlength': '50'}))


class TemplateForm(forms.Form):
    topic_name = forms.CharField(widget=forms.Select(
        attrs={'class': 'form-control'}))

    # topic = forms.CharField(widget=forms.Select(choices=topic_choices(),
    #     attrs={'class': 'form-control'}))
    template_name = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'30'}))
    default_message = forms.CharField(max_length=160, widget=forms.Textarea(
        attrs={'class':'form-control','maxlength':'160'}))


class TopicForm(forms.Form):
    topic_name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'100'}))
    display_name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class':'form-control','maxlength':'100'}))
    topic_owner = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.Select(
        attrs={'class': 'form-control'}))


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