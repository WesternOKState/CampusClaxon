from django.test import TestCase
from AlertAdmin.models import Subscriber, MessageLog, TopicSubscription, Setting, Topic, Template
from CampusClaxon.lib import get_hash
from django.contrib.auth.models import User, Group
from django.urls import reverse
import datetime
from django.test import Client
from CampusClaxon.AmazonMessage import AmazonMessage
# Create your tests here.


class AdminTest(TestCase):

    def __init__(self, *args):
        super(AdminTest, self).__init__(*args)
        self.url = reverse('index2')


    def setUp(self):
        amz_security_key = 'AKIAJ4CHLKIWZBPPC2XQ'
        amz_secret_key = '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'
        setting = Setting.objects.create(aws_security_key=amz_security_key, aws_secret_key=amz_secret_key)
        setting.save()
        sub = Subscriber()
        sub.first_name = "Fred"
        sub.last_name = "Flinstone"
        sub.student_id = "123001234"
        sub.school_email = "fred.flinstone@email.wosc.edu"
        sub.personal_email = "fred.flinstone@wosc.edu"
        sub.cell_phone = "15803011758"
        sub.save()
        user = User.objects.create_user(username='fred.flinstone', password='testitout', first_name="Fred", last_name="Flinstone")
        group = Group.objects.create(name='admin')
        user.groups.add(group)
        if not self.client.login(username='fred.flinstone', password='testitout'):
            raise ValueError("User not logged in for some reason")
        session = self.client.session
        session['source_id'] = sub.hash
        session.save()
        messageLog = MessageLog()
        messageLog.initiator = User.objects.all()[0]
        messageLog.topic_name = "arn:aws:sns:us-east-1:XXXXXXXXXXXX:TestTopicName"
        messageLog.message = "Test topic message."
        messageLog.timestamp = datetime.datetime.now()
        messageLog.save()

        topic = Topic.objects.create(topic_name="TestTopicName", topic_arn="arn:aws:sns:us-east-1:XXXXXXXXXXXX:TestTopicName",
                             topic_type="public", topic_owner=User.objects.all()[0])
        Topic.objects.create(topic_name="NotSubscribedTopic",
                             topic_arn="arn:aws:sns:us-east-1:XXXXXXXXXXXX:NotSubscribedTopic",
                             topic_type="public", topic_owner=User.objects.all()[0])
        TopicSubscription.objects.create(subscriber=Subscriber.objects.get(hash=sub.hash),
                                         subscription_arn='arn:aws:sns:us-east-1:XXXXXXXXXXXX:TestTopicName:00000000-0000-0000-0000-000000000000',
                                         status="active", topic=Topic.objects.get(topic_name="TestTopicName"))
        MessageLog.objects.create(initiator=User.objects.all()[0],
                                  topic_name="arn:aws:sns:us-east-1:XXXXXXXXXXXX:NotSubscribedTopic",
                                  message="This is another test message", timestamp= datetime.datetime.now())
        Template.objects.create(topic_name=topic.topic_name, template_name="Stuff and things alert.", default_message="This is a default message.")

        self.amz = AmazonMessage(amz_security_key,amz_secret_key)


    def test_bad_users_have_no_access(self):
        c = Client()
        res = c.get(self.url)
        self.assertEqual(res.status_code, 403)

    def test_valid_users_have_access(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)


class AlertAdminIndexTest(AdminTest):

    def __init__(self, *args):
        super(AlertAdminIndexTest, self).__init__(*args)
        self.url = reverse('index2')


class SendAlertPageTest(AdminTest):

    def __init__(self, *args):
        super(SendAlertPageTest, self).__init__(*args)
        self.url = reverse('Send Alert')

    def test_check_for_template_functionality(self):
        template = Template.objects.all()[0]

        res = self.client.get(self.url, {'pk': template.id})
        self.assertContains(res, 'Stuff and things alert.', 1, 200)

    def test_the_sending_of_a_message(self):
        # actually create the topic and subscription
        topic = Topic.objects.all()[0]
        topic_arn = self.amz.create_topic(topic.topic_name)
        topic_subscription = self.amz.subscribe('15803011758', topic_arn)
        sub = TopicSubscription.objects.get(topic=topic)
        sub.subscription_arn= topic_subscription
        sub.save()
        res = self.client.post(self.url, data={'topic': topic.id, 'message': 'This is a test message'})
        self.assertEquals(res.status_code, 200)