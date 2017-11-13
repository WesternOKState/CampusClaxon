import hashlib
from .settings import SECRET_KEY
import AlertAdmin.models
# from CampusClaxon.SMSManager import AmazonMessage
from CampusClaxon.SMSManager import SMSManager
from django.views.generic import TemplateView, FormView, ListView
import re

def get_hash(sid):
    sid = re.sub("[-]", '', sid)
    return hashlib.sha224("{}{}".format(sid, SECRET_KEY).encode('utf-8')).hexdigest()


def get_topic_subscribers(topic_arn):
    mySettings = AlertAdmin.models.Setting.objects.get(pk=1)
    amazon = AmazonMessage(mySettings.security_key, mySettings.secret_key)
    amz_subs = amazon.get_subscribers(topic_arn)
    lcl_subs = AlertAdmin.models.Subscriber.objects.all()
    # To attempt efficiency, we are going to try to create a dic from the user data, keyed on the phone number
    users = {}
    for sub in lcl_subs:
        users[sub.cell_phone] = {'last_name': sub.last_name, 'first_name': sub.first_name,
                                  'student_id': sub.student_id, 'school_email': sub.school_email,
                                  'personal_email': sub.personal_email, 'cell_phone': sub.cell_phone}
    # now lets return the info for the relevant users:
    res = []
    for sub in amz_subs:
        endpoint = sub['endpoint']
        if endpoint[0] == '+' : endpoint = endpoint[1:]
        users[endpoint]['SubscriptionArn'] = sub['SubscriptionArn']
        res.append(users[endpoint])
    print(res)
    return res

def processFile(file, topic):
    for line in file:
        line = line.strip()
        line = line.split(',')
        if line[0].lower() != "studentid":
            if len(line) == 6:
                if not AlertAdmin.models.Subscriber.objects.filter(cell_phone=line[1]).exists():
                    subscriber = AlertAdmin.models.Subscriber()
                    subscriber.cell_phone = line[1]
                else:
                    subscriber = AlertAdmin.models.Subscriber.objects.get(cell_phone=line[1])
                subscriber.student_id = line[0]
                subscriber.personal_email = line[2]
                subscriber.school_email = line[3]
                subscriber.last_name = line[4]
                subscriber.first_name = line[5]
                subscriber.save()
                if not AlertAdmin.models.TopicSubscription.objects.filter(topic=topic, subscriber__cell_phone=line[1]):
                    sub = AlertAdmin.models.TopicSubscription()
                    sub.subscriber = AlertAdmin.models.Subscriber.objects.get(cell_phone=line[1])
                    sub.topic = topic
                    sub.status = 'active'
                    sub.save()

def change_cell_number(hash, new_num):
    subscriber = AlertAdmin.models.Subscriber.objects.get(hash=hash)
    topic_subscriptions = AlertAdmin.models.TopicSubscription.objects.filter(subscriber=subscriber, status='active')
    mysettings = AlertAdmin.models.Setting.objects.all()[0]
    sms = SMSManager()
    for subscription in topic_subscriptions:
        res = sms.unsubscribe(subscription.subscription_arn)
        if res != 0: return "Unable to unsubscribe from " + subscription.topic.topic_name
        topic = subscription.topic.topic_arn
        res = sms.subscribe(new_num,topic)
        if res == 0: return "Unable to subscribe to " + topic.topic_name
        new_subscription = AlertAdmin.models.TopicSubscription()
        new_subscription.subscriber = subscriber
        new_subscription.subscription_arn = subscription.subscription_arn
        new_subscription.status = 'active'
        new_subscription.topic = AlertAdmin.models.Topic.objects.get(topic_arn=topic)
        new_subscription.save()
        subscription.delete()

    subscriber.cell_phone = new_num
    subscriber.save()
    return 0


def get_theme(template):
    theme_name = 'base/' + template
    return theme_name

class AlertTemplateView(TemplateView):

    def __init__(self):
        self.template_name = get_theme(self.template_name)
        return super(AlertTemplateView, self).__init__()

    def get_context_data(self, **kwargs):
        context = super(AlertTemplateView, self).get_context_data()
        context['theme'] = AlertAdmin.models.Setting.objects.all()[0].theme_name
        return context


class AlertFormView(FormView):

    def __init__(self):
        self.template_name = get_theme(self.template_name)
        return super(AlertFormView, self).__init__()

    def get_context_data(self, **kwargs):
        context = super(AlertFormView, self).get_context_data()
        context['theme'] = AlertAdmin.models.Setting.objects.all()[0].theme_name
        return context

class AlertListView(ListView):

    def __init__(self):
        self.template_name = get_theme(self.template_name)
        return super(AlertListView, self).__init__()

    def get_context_data(self, **kwargs):
        context = super(AlertListView, self).get_context_data()
        context['theme'] = AlertAdmin.models.Setting.objects.all()[0].theme_name
        return context


def add_new_subscriber(first_name, last_name, student_id, school_email):
    print("Adding Subscriber...")
    mySubscriber = AlertAdmin.models.Subscriber()
    mySubscriber.first_name = first_name
    mySubscriber.last_name = last_name
    mySubscriber.cell_phone = ""
    mySubscriber.student_id = student_id
    mySubscriber.personal_email = ""
    mySubscriber.school_email = school_email
    mySubscriber.save()
    subscribe_to_public(mySubscriber)
    subscribe_to_required(mySubscriber)
    return mySubscriber

def subscribe_to_public(subscriber):
    print("Subscribing to public:")
    topics = AlertAdmin.models.Topic.objects.filter(topic_type="public")
    for topic in topics:
        if not AlertAdmin.models.TopicSubscription.objects.filter(topic=topic, subscriber=subscriber).exists():
            sms = SMSManager()
            subscription_arn = sms.subscribe(subscriber.hash, topic.topic_arn)
            subscription = AlertAdmin.models.TopicSubscription()
            print(topic.topic_name)
            subscription.subscriber = subscriber
            subscription.topic = topic
            subscription.status = 'disabled'
            subscription.subscription_arn = subscription_arn
            subscription.save()
    return 0

def subscribe_to_required(subscriber):
    print("Subscribing to required:")
    topics = AlertAdmin.models.Topic.objects.filter(topic_type="required")
    for topic in topics:
        if not AlertAdmin.models.TopicSubscription.objects.filter(topic=topic, subscriber=subscriber).exists():
            sms = SMSManager()
            subscription_arn = sms.subscribe(subscriber.hash, topic.topic_arn)
            print(topic.topic_name)
            mysettings = AlertAdmin.models.Setting.objects.get(pk=1)
            sms = SMSManager()
            res = sms.subscribe(subscriber.cell_phone, topic.topic_arn)
            print("Required: " + res)
            if res != 0:
                subscription = AlertAdmin.models.TopicSubscription()
                subscription.subscriber = subscriber
                subscription.topic = topic
                subscription.status = 'active'
                subscription.subscription_arn = subscription_arn
                subscription.save()
                return res
            else:
                return 0