from .AmazonMessage import AmazonMessage
from .NexmoMessage import NexmoMessage

import AlertAdmin.models
# from AlertAdmin.models import Setting, Topic, Subscriber, MessageLog
import datetime

class SMSManager():

    def __init__(self):
        settings = AlertAdmin.models.Setting.objects.all()[0]
        self.sms_provider = settings.sms_provider
        self.sms = None
        if self.sms_provider == "amazon":
            self.sms = AmazonMessage(settings.security_key, settings.secret_key)
        if self.sms_provider == 'nexmo':
            self.sms = NexmoMessage(settings.security_key, settings.secret_key)

    def send_single_message(self, number, message, template=0):
        res = self.sms.send_single_message(number, message, template)



    def send_message(self, message, topic):
        res = self.sms.send_message(message, topic.topic_arn)
        if res == True:
            # message_log = MessageLog()
            # message_log.initiator = self.request.user
            # message_log.topic_name = self.request.POST['topic']
            # message_log.message = self.request.POST['message']
            # message_log.timestamp = datetime.datetime.now()
            # message_log.save()
            print("done did it")

    def send_bulk_message(self, message, topic, template=0, **kwargs):
        res = self.sms.send_bulk_message(message, topic.topic_arn, template, **kwargs)
        if res == True:
            # message_log = MessageLog()
            # message_log.initiator = self.request.user
            # message_log.topic_name = self.request.POST['topic']
            # message_log.message = self.request.POST['message']
            # message_log.timestamp = datetime.datetime.now()
            # message_log.save()
            print("done did it")


    def get_subscribers(self, topic):
        if self.sms_provider == 'amazon':
            return self.sms.get_subscribers(topic.topic_arn)
        if self.sms_provider == 'nexmo':
            pass

    def subscribe(self, user_hash, topic):
        return self.sms.subscribe(user_hash, topic)

    def add_to_topic_list(self, user_hash, topic):
        return self.sms.add_to_topic_list(user_hash, topic)

    def unsubscribe(self, subscription_arn):
            return self.sms.unsubscribe(subscription_arn)

    def create_topic(self, topic_name, display_name, instructor):
        return self.sms.create_topic(topic_name, display_name, instructor)

    def get_topics(self):
        if self.sms_provider == "amazon":
            return self.sms.get_topics()
        if self.sms_provider == "nexos":
            pass

    def set_topic_attributes(self, topic, display_name):
        if self.sms_provider == "amazon":
            return self.sms.set_topic_attributes(topic, topic.topic_arn, display_name)
        if self.sms_provider == "nexos":
            pass

    def delete_topic(self, topic):
        if self.sms_provider == "amazon":
            return self.sms.set_topic_attributes(topic, topic.topic_arn)
        if self.sms_provider == "nexos":
            pass

    def get_initial_settings(self):
        s = Setting.objects.all()[0]

        results = {
            'theme_name': s.theme_name,
            'quick_alert_auth_code': s.quick_alert_auth_code,
            'globaltopic': s.global_topic,
            'security_key': s.security_key,
            'secret_key': s.secret_key,
            'sms_provider': s.sms_provider,
        }
        return results


    def set_settings(self, settings):
        mySettings = AlertAdmin.models.Setting(pk=1)
        mySettings.theme_name = settings['theme_name']
        mySettings.authentication_type = settings['authentication_type']
        mySettings.quick_alert_auth_code = settings['quick_alert_auth_code']
        mySettings.global_topic = AlertAdmin.models.Topic.objects.get(id=settings['globaltopic'])
        mySettings.sms_provider = settings['sms_provider']
        mySettings.security_key = settings['security_key']
        mySettings.secret_key = settings['secret_key']
        mySettings.save()

