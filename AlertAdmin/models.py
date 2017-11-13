from django.db import models
from django.contrib.auth.models import User
from CampusClaxon.lib import get_hash


# Create your models here.

TOPIC_TYPE_CHOICES = (
    ('select', 'Select'),
    ('public', 'Public'),
    ('private', 'Private'),
    ('required', 'Required'),
)

SUBSCRIBER_STATUS_CHOICES = (
    ( 'select', 'Select'),
    ('active', 'Active'),
    ('disabled', 'Disabled'),
)

AUTH_CHOICES = (
    ('internal', 'Internal'),
    ('lti', 'LTI'),
)


SMS_PROVIDER_CHOICES = (
    ('amazon', 'Amazon'),
    ('nexmo', "Nexmo"),
)

class Subscriber(models.Model):
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    cell_phone = models.CharField(max_length=30, null=True, blank=True)
    student_id = models.CharField(max_length=30)
    school_email = models.CharField(max_length=50, null=True, blank=True)
    personal_email = models.CharField(max_length=50, null=True, blank=True)
    hash = models.CharField(max_length=56, default='', null=True, blank=True)
    opt_out = models.NullBooleanField(null=True, blank=True)

    def save(self):
        self.hash = get_hash(self.student_id)
        super(Subscriber, self).save()

    def __str__(self):
        return self.last_name + " " + self.first_name


class ResultsLog(models.Model):
    message_count = models.IntegerField()
    messages = models.CharField(max_length=2048)
    status = models.CharField(max_length=128)
    message_id = models.CharField(max_length=16)
    to = models.CharField(max_length=16)
    client_ref = models.CharField(max_length=40)
    remaining_balance = models.CharField(max_length=16)
    message_price = models.CharField(max_length=16)
    network = models.CharField(max_length=40)
    error_text = models.CharField(max_length=1024)
    time_Stamp = models.DateTimeField()

    def __str__(self):
        return str(self.to)


class MessageLog(models.Model):
    initiator = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now=True)
    message = models.CharField(max_length=160)
    topic_name = models.CharField(max_length=150)

    def __str__(self):
        return self.message


class Topic(models.Model):

    topic_name = models.CharField(max_length=30)
    topic_arn = models.CharField(max_length=100, unique=True)
    topic_type = models.CharField(max_length=100, choices=TOPIC_TYPE_CHOICES, default="public")
    description = models.CharField(max_length=1024, default="Enter Topic Description Here.")
    topic_owner = models.ForeignKey(User)
    display_name = models.CharField(max_length=12, default="wosc")

    def __str__(self):
        return self.topic_name


class Setting(models.Model):
    security_key = models.CharField(max_length=50)
    secret_key = models.CharField(max_length=150)
    theme_name = models.CharField(max_length=50)
    authentication_type = models.CharField(max_length=100, choices=AUTH_CHOICES, default="internal")
    quick_alert_auth_code= models.CharField(max_length=100)
    global_topic = models.ForeignKey(Topic)
    sms_provider = models.CharField(max_length=100, choices=SMS_PROVIDER_CHOICES)

    def __str__(self):
        return str(self.theme_name + " " + self.sms_provider)

class TopicSubscription(models.Model):
    subscriber = models.ForeignKey("Subscriber")
    subscription_arn = models.CharField(max_length=150)
    status = models.CharField(max_length=150, choices=SUBSCRIBER_STATUS_CHOICES)
    topic = models.ForeignKey(Topic)

    def __str__(self):
        return self.subscriber.first_name + " " + self.subscriber.last_name + " - " + self.topic.topic_name + \
               " - " + self.status


class Template(models.Model):
    topic = models.ForeignKey(Topic)
    template_name = models.CharField(max_length=30)
    default_message = models.CharField(max_length=160)

    def __str__(self):
        return self.template_name
