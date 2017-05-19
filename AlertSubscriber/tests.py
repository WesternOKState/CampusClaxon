from django.test import TestCase
from AlertAdmin.models import Subscriber, MessageLog, TopicSubscription, Setting, Topic
from CampusClaxon.lib import get_hash
from django.contrib.auth.models import User, Group
from django.urls import reverse
import datetime
from django.test import Client
from CampusClaxon.AmazonMessage import AmazonMessage
# Create your tests here.


class SubscribeTest(TestCase):

    def __init__(self, *args):
        super(SubscribeTest, self).__init__(*args)
        self.url = reverse('index')


# Fill in the required info to get this tests to work

    def setUp(self):
        # Required
        amz_security_key = ''
        # Required
        amz_secret_key = ''
        setting = Setting.objects.create(aws_security_key=amz_security_key, aws_secret_key=amz_secret_key)
        setting.save()
        sub = Subscriber()
        sub.first_name = "Fred"
        sub.last_name = "Flinstone"
        sub.student_id = "123001234"
        sub.school_email = "fred.flinstone@email.wosc.edu"
        sub.personal_email = "fred.flinstone@wosc.edu"
        sub.cell_phone = "15805551212"
        sub.save()
        user = User.objects.create_user(username='fred.flinstone', password='testitout', first_name="Fred", last_name="Flinstone")
        group = Group.objects.create(name='subscriber')
        user.groups.add(group)
        if not self.client.login(username='fred.flinstone', password='testitout'):
            raise ValueError("User not logged in for some reason")
        session = self.client.session
        session['source_id'] = sub.hash
        session.save()
        messageLog = MessageLog()
        messageLog.initiator = User.objects.all()[0]
        # Required
        messageLog.topic_name = "arn:aws:sns:us-east-1:XXXXXXXXXXXX:TestTopicName"
        messageLog.message = "Test topic message."
        messageLog.timestamp = datetime.datetime.now()
        messageLog.save()
        Topic.objects.create(topic_name="TestTopicName", topic_arn="arn:aws:sns:us-east-1:XXXXXXXXXXXX:TestTopicName",
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

        self.amz = AmazonMessage(amz_security_key,amz_secret_key)


    def test_bad_users_have_no_access(self):
        c = Client()
        res = c.get(self.url)
        self.assertEqual(res.status_code, 403)

    def test_valid_users_have_access(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)


class IndexTestCase(SubscribeTest):

    def __init__(self, *args):
        super(SubscribeTest, self).__init__(*args)
        self.url = reverse('index')

    def test_if_send_message_shows_correctly(self):
        res = self.client.get(self.url)
        # Make sure 'Send an alert' is not showing for students
        self.assertNotContains(res,'Send An Alert', 200)
        # Add Fred to instructor group
        user = User.objects.get(username=res.context['user'])
        gp = Group.objects.create(name='instructor')
        user.groups.add(gp)
        res = self.client.get(self.url)
        # Check to make sure the button is available
        self.assertContains(res, 'Send An Alert', 2, 200)


class SendMessageViewTestCase(SubscribeTest):

    def __init__(self, *args):
        super(SubscribeTest, self).__init__(*args)
        self.url = reverse('send_message')

    def test_only_instructors_can_access(self):
        res = self.client.get(self.url)
        self.assertEquals(res.status_code, 403)
        user = User.objects.get(username='fred.flinstone')
        gp = Group.objects.create(name='instructor')
        user.groups.add(gp)
        res = self.client.get(self.url)
        self.assertEquals(res.status_code, 200)

    def test_valid_users_have_access(self):
        self.assertEquals(1,1)



class ManageAccountTestCase(SubscribeTest):

    def __init__(self, *args):
        super(SubscribeTest, self).__init__(*args)
        self.url = reverse('manageAccount')


class ManageUserGroupsTestCase(SubscribeTest):

    def __init__(self, *args):
        super(SubscribeTest, self).__init__(*args)
        self.url = reverse('manageUserGroups')


class ViewLogsTestCase(SubscribeTest):

    def __init__(self, *args):
        super(SubscribeTest, self).__init__(*args)
        self.url = reverse('viewLogs')

    def test_if_user_can_see_logs(self):
        res = self.client.get(self.url)
        self.assertContains(res,'TestTopicName', 1, 200)


    def test_if_user_cannot_see_other_logs(self):
        res = self.client.get(self.url)
        self.assertNotContains(res, 'NotSubscribedTopic', 200)


class EditSubscriberCellPhoneTestCase(SubscribeTest):

    def __init__(self, *args):
        super(SubscribeTest, self).__init__(*args)
        self.url = reverse('edit_subscriber_cell_phone')

    def test_bad_users_have_no_access(self):
        c = Client()
        res = c.post(self.url, {'new_number': '15805553333', 'old_number' : '15805552125' })
        self.assertEqual(res.status_code, 403)

    def test_valid_users_have_access(self):
        # Reset the database info
        Topic.objects.get(topic_name="TestTopicName").delete()
        # TopicSubscription.objects.get(subscription_arn='arn:aws:sns:us-east-1:XXXXXXXXXXXX:TestTopicName:00000000-0000-0000-0000-000000000000').delete()

        sub = Subscriber.objects.get(hash=self.client.session['source_id'])
        self.topic_arn = self.amz.create_topic("TestTopicForTests")
        self.subscription_arn = self.amz.subscribe(sub.cell_phone, self.topic_arn)
        topic = Topic.objects.create(topic_name="testTopicForTests", topic_arn=self.topic_arn, topic_type='public',
                                     description="This is a description", topic_owner=User.objects.all()[0])
        TopicSubscription.objects.create(subscriber=sub, subscription_arn=self.subscription_arn, status="active", topic=topic)
        res = self.client.post(self.url, {'new_number': '15803333333', 'old_number': sub.cell_phone})
        self.assertEqual(res.url, reverse('manageAccount'))
        self.amz.unsubscribe(self.subscription_arn)
        self.amz.delete_topic(self.topic_arn)

class SubscribeTestCase(SubscribeTest):

    def __init__(self, *args):
        super(SubscribeTest, self).__init__(*args)
        self.url = reverse('subscribe')

    def test_bad_users_have_no_access(self):
        c = Client()
        res = c.post(self.url, {'new_number': '15803333333', 'old_number' : '15805555758' })
        self.assertEqual(res.status_code, 403)

    def test_valid_users_have_access(self):
        self.topic_arn = self.amz.create_topic("TestTopicForTests")
        topic = Topic()
        topic.name = "TestTopicForTests"
        topic.topic_arn = self.topic_arn
        topic.topic_type = "public"
        topic.description = "test"
        topic.topic_owner = User.objects.all()[0]
        topic.save()
        res = self.client.post(self.url, {'id': topic.id})
        self.assertEqual(res.url, reverse('manageUserGroups'))
        self.amz.delete_topic(self.topic_arn)


class UnsubscribeTestCase(SubscribeTest):

    def __init__(self, *args):
        super(SubscribeTest, self).__init__(*args)
        self.url = reverse('unsubscribe')

    def test_bad_users_have_no_access(self):
        c = Client()
        res = c.post(self.url, {'new_number': '15803333333', 'old_number' : '15805551758' })
        self.assertEqual(res.status_code, 403)

    def test_valid_users_have_access(self):
        sub = Subscriber.objects.get(hash=self.client.session['source_id'])
        self.topic_arn = self.amz.create_topic("TestTopicForTests")
        topic = Topic()
        topic.name = "TestTopicForTests"
        topic.topic_arn = self.topic_arn
        topic.topic_type = "public"
        topic.description = "test"
        topic.topic_owner = User.objects.all()[0]
        topic.save()
        self.subscription_arn = self.amz.subscribe(sub.cell_phone, self.topic_arn)
        TopicSubscription.objects.create(subscriber=sub, subscription_arn=self.subscription_arn, status="active", topic=topic)
        res = self.client.post(self.url, {'id': topic.id, 'subscription_arn': self.subscription_arn})
        self.assertEqual(res.url, reverse('manageUserGroups'))
        self.amz.unsubscribe(self.subscription_arn)
        self.amz.delete_topic(self.topic_arn)