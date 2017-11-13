import requests
from time import sleep
# from AlertAdmin.models import TopicSubscription, Topic
import AlertAdmin.models
from django.contrib.auth.models import User

class NexmoMessage:

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def create_topic(self, topic_name, display_name, instructor):
        myTopic = AlertAdmin.models.Topic()
        myTopic.topic_name = topic_name
        myTopic.topic_arn = topic_name
        myTopic.topic_owner = instructor
        myTopic.description = "Optional group to receive notifications from {} class.".format(display_name)
        myTopic.topic_type = 'private'
        myTopic.display_name = display_name + ">"
        myTopic.save()
        return myTopic.id

    def send_single_message(self, number, message, template):

        url = 'https://rest.nexmo.com/sc/us/alert/json'
        s = requests.Session()

        if template == 0:
            data = {
                'api_key': self.key,
                'api_secret': self.secret,
                'to': number,
                'from': '12013711448',
                'template': '2',
                'msg': message,
                'client-ref': 'wosc-alert'
            }
            print('------------')
            print("\n{}\n".format(data['to']))
            r = s.post(url, data)

        if template == 5:
            data = {
                'api_key': self.key,
                'api_secret': self.secret,
                'to': number,
                'from': '12013711448',
                'template': '5',
                'client-ref': 'wosc-alert'
            }
            print('------------')
            print("\n{}\n".format(data['to']))
            r = s.post(url, data)




    def send_message(self, message, topicArn):
        '''
        Sends message to every one subscribed to the topicArn
        :param message: The message to send
        :param topicArn: The topic to send it to.
        :return: True if successful HTTP error if unsuccessful
        '''
        url = 'https://rest.nexmo.com/sms/json'
        topic = AlertAdmin.models.Topic.objects.get(topic_arn=topicArn)
        subs = AlertAdmin.models.TopicSubscription.objects.filter(topic=topic)
        message = topic.display_name  + message
        s = requests.Session()
        for sub in subs:
            data = {
                'api_key': self.key,
                'api_secret': self.secret,
                'text': message,
                'to': sub.subscriber.cell_phone,
                'from': '12013711448',
            }
            print("\n{}\n".format(data['to']))
            r = s.post(url, data)
            sleep(1)
        return True

    def send_bulk_message(self, message, topicArn, template, **kwargs):
        '''
        Sends message to every one subscribed to the topicArn
        :param message: The message to send
        :param topicArn: The topic to send it to.
        :return: True if successful HTTP error if unsuccessful
        '''


        if template == 1:
            #
            self._send_template_1(kwargs['close_time'], kwargs['reason'], topicArn)

        if template == 2:
            self._send_template_2(message, topicArn)

        if template == 3:
            self._send_template_3(topicArn)

        if template == 4:
            self._send_template_4(kwargs['close_time'], topicArn)

        if template == 5:
            self._send_template_5(topicArn)

        if template == 6:
            self._send_template_6(kwargs['close_time'], kwargs['reason'], topicArn)

        return True

    @staticmethod
    def subscribe(user_hash, topic_arn):
        return user_hash + topic_arn

    def add_to_topic_list(self, user_hash, topic_arn):

        if not AlertAdmin.models.TopicSubscription.objects.filter(
                subscriber__hash=user_hash, topic__topic_arn=topic_arn).exists():
            subscripton = AlertAdmin.models.TopicSubscription()
            subscripton.subscriber = AlertAdmin.models.Subscriber.objects.get(hash=user_hash)
            subscripton.subscription_arn = user_hash + topic_arn.topic_arn
            subscripton.status = "disabled"
            subscripton.topic = AlertAdmin.models.Topic.objects.get(topic_arn=topic_arn)
            subscripton.save()
        return user_hash + topic_arn.topic_arn

    def unsubscribe(self, subscription_arn):
        subscription = AlertAdmin.models.TopicSubscription.objects.get(subscription_arn=subscription_arn)
        subscription.status = "disabled"
        subscription.save()
        return 1


    def _send_template_5(self, topicArn):
        url = 'https://rest.nexmo.com/sc/us/alert/json'
        topic = AlertAdmin.models.Topic.objects.get(topic_arn=topicArn)
        subs = AlertAdmin.models.TopicSubscription.objects.filter(topic=topic).filter(subscriber__cell_phone__isnull=False)
        log_entry = AlertAdmin.models.MessageLog()
        log_entry.message = "Welcome to WOSC-Alert. We will only use this for cancellations, " \
                            "weather and other very important info. Want to opt-out? Reply STOP"
        log_entry.initiator = User.objects.get(username="admin")
        log_entry.topic_name = topic.topic_name
        log_entry.save()
        print("SEND TEMPLATE 5")
        count = 0
        s = requests.Session()
        for sub in subs:
            data = {
                'api_key': self.key,
                'api_secret': self.secret,
                'to': sub.subscriber.cell_phone,
                'from': '12013711448',
                'template': '5',
                'client-ref': str(log_entry.id)
            }
            print('------------')
            print("\n{}\n".format(data['to']))
            r = s.post(url, data)
            sleep(.04)
            count += 1
        print("Sent {} messages".format(count))
        return

    def _send_template_3(self, topicArn):
        url = 'https://rest.nexmo.com/sc/us/alert/json'
        topic = AlertAdmin.models.Topic.objects.get(topic_arn=topicArn)
        subs = AlertAdmin.models.TopicSubscription.objects.filter(topic=topic)
        print("SEND TEMPLATE 6")
        log_entry = AlertAdmin.models.MessageLog()
        log_entry.message = "Western is experiencing power outages and classes are temporarily suspended. " \
                            "Msg will be sent when classes resume."
        log_entry.initiator = User.objects.get(username="admin")
        log_entry.topic_name = topic.topic_name
        log_entry.save()
        s = requests.Session()
        for sub in subs:
            data = {
                'api_key': self.key,
                'api_secret': self.secret,
                'to': sub.subscriber.cell_phone,
                'from': '12013711448',
                'template': '3',
                'client-ref': str(log_entry.id)
            }
            print('------------')
            print("\n{}\n".format(data['to']))
            r = s.post(url, data)
            sleep(.04)
        return

    def _send_template_1(self, close_time, reason, topicArn):
        url = 'https://rest.nexmo.com/sc/us/alert/json'
        topic = AlertAdmin.models.Topic.objects.get(topic_arn=topicArn)
        subs = AlertAdmin.models.TopicSubscription.objects.filter(topic=topic)
        print("SEND TEMPLATE 6")
        log_entry = AlertAdmin.models.MessageLog()
        log_entry.message = '''Online courses are not accessible due to {},
    we hope to restore service before {}'''.format(reason, close_time)
        log_entry.initiator = User.objects.get(username="admin")
        log_entry.topic_name = topic.topic_name
        log_entry.save()
        s = requests.Session()
        for sub in subs:
            data = {
                'api_key': self.key,
                'api_secret': self.secret,
                'time': close_time,
                'reason': reason,
                'to': sub.subscriber.cell_phone,
                'from': '12013711448',
                'template': '1',
                'client-ref': str(log_entry.id)
            }
            print('------------')
            print("\n{}\n".format(data['to']))
            r = s.post(url, data)
            sleep(.04)
        return

    def _send_template_6(self, close_time, reason, topicArn):
        url = 'https://rest.nexmo.com/sc/us/alert/json'
        topic = AlertAdmin.models.Topic.objects.get(topic_arn=topicArn)
        subs = AlertAdmin.models.TopicSubscription.objects.filter(topic=topic)
        print("SEND TEMPLATE 6")
        log_entry = AlertAdmin.models.MessageLog()
        log_entry.message = '''Western will be closing at {} due to {}'''.format(close_time, reason)
        log_entry.initiator = User.objects.get(username="admin")
        log_entry.topic_name = topic.topic_name
        log_entry.save()
        s = requests.Session()
        for sub in subs:
            data = {
                'api_key': self.key,
                'api_secret': self.secret,
                'time': close_time,
                'reason': reason,
                'to': sub.subscriber.cell_phone,
                'from': '12013711448',
                # 'template': '4',
                'client-ref': str(log_entry.id)
            }
            print('------------')
            print("\n{}\n".format(data['to']))
            r = s.post(url, data)
            sleep(.04)
        return

    def _send_template_4(self,  close_time, topicArn):
        url = 'https://rest.nexmo.com/sc/us/alert/json'
        topic = AlertAdmin.models.Topic.objects.get(topic_arn=topicArn)
        subs = AlertAdmin.models.TopicSubscription.objects.filter(topic=topic)
        print("SEND TEMPLATE 1")
        log_entry = AlertAdmin.models.MessageLog()
        log_entry.message = '''Welcome to WOSC-Alert. We will only use this for cancellations,
    weather and other dangerous situationsDue to severe weather,
    Western will be closed at ${time}.
    Be sure that you are in a safe place and watch wosc.edu for details.'''.format(close_time)
        log_entry.initiator = User.objects.get(username="admin")
        log_entry.topic_name = topic.topic_name
        log_entry.save()

        s = requests.Session()
        for sub in subs:
            data = {
                'api_key': self.key,
                'api_secret': self.secret,
                'time': close_time,
                'to': sub.subscriber.cell_phone,
                'from': '12013711448',
                'template': '4',
                'client-ref': str(log_entry.id)
            }
            print('------------')
            print("\n{}\n".format(data['to']))
            r = s.post(url, data)
            sleep(.04)
        return

    def _send_template_2(self,  message, topicArn):
        url = 'https://rest.nexmo.com/sc/us/alert/json'
        topic = AlertAdmin.models.Topic.objects.get(topic_arn=topicArn)
        subs = AlertAdmin.models.TopicSubscription.objects.filter(topic=topic)
        log_entry = AlertAdmin.models.MessageLog()
        log_entry.message = message
        log_entry.initiator = User.objects.get(username="admin")
        log_entry.topic_name = topic.topic_name
        log_entry.save()

        s = requests.Session()
        for sub in subs:
            data = {
                'api_key': self.key,
                'api_secret': self.secret,
                'msg': message,
                'to': sub.subscriber.cell_phone,
                'from': '12013711448',
                'template': '2',
                'client-ref': str(log_entry.id)
            }
            print('------------')
            print("\n{}\n".format(data['to']))
            r = s.post(url, data)
            sleep(.04)
        return