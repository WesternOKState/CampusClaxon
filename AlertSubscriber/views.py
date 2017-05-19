import re
from braces.views import GroupRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import View
from django.contrib.auth.models import User
from AlertAdmin.models import Subscriber, Topic, TopicSubscription, Setting, MessageLog
from CampusClaxon.AmazonMessage import AmazonMessage
from .forms import SubscriberForm, MyMessageForm
from CampusClaxon.lib import change_cell_number, AlertTemplateView, AlertFormView



class SubscriberMixin(GroupRequiredMixin):
    group_required = 'subscriber'
    redirect_unauthenticated_users = '/login/'

class IndexView(SubscriberMixin, AlertTemplateView):
    template_name = 'AlertSubscriber/index.html'

    def get_context_data(self, **kwargs):
        if Setting.objects.all()[0].authentication_type == 'internal':
            user = User.objects.get(username=self.request.user)
            self.request.session['source_id'] = Subscriber.objects.get(school_email=user.email).hash
        return super(IndexView, self).get_context_data(**kwargs)


class ManageAccountView(SubscriberMixin, AlertFormView):
    template_name = "AlertSubscriber/editSubscriber.html"
    form_class = SubscriberForm

    def get_initial(self):
        initial = super(ManageAccountView, self).get_initial()
        sub = Subscriber.objects.get(hash=self.request.session['source_id'])
        initial['first_name'] = sub.first_name
        initial['last_name'] = sub.last_name
        initial['personal_email'] = sub.personal_email
        if sub.opt_out:
            initial['opt_out'] = "on"
        else:
            initial['opy_out'] = "off"
        return initial

    def get_context_data(self, **kwargs):
        # TODO See if I can supply this info in get_initial
        print("test")
        context = super(ManageAccountView, self).get_context_data(**kwargs)
        sub = Subscriber.objects.get(hash=self.request.session['source_id'])
        cell_phone = "{}({}){}-{}".format(sub.cell_phone[0], sub.cell_phone[1:4], sub.cell_phone[4:7],
                                          sub.cell_phone[7:])
        context['cell_phone'] = cell_phone
        student_id = Subscriber.objects.get(hash=self.request.session['source_id']).student_id
        context['student_id'] = "{}-{}".format(student_id[:4],student_id[5:])
        context['first_name'] = sub.first_name
        context['last_name'] = sub.last_name
        context['personal_email'] = sub.personal_email
        context['school_email'] = sub.school_email
        context['authentication_type'] = Setting.objects.all()[0].authentication_type
        print("BLAH:" + context['authentication_type'])
        return context

    def form_valid(self, form):
        sub = Subscriber.objects.get(hash=self.request.session['source_id'])
        sub.personal_email = self.request.POST['personal_email']
        if 'opt_out' in self.request.POST:
            sub.opt_out = True
        else:
            sub.opt_out = False
        sub.save()
        if Setting.objects.all()[0].authentication_type == 'internal':
            if self.request.POST['password'] != '':
                user = User.objects.get(username=self.request.user)
                user.set_password(self.request.POST['password'])
                user.save()
        self.success_url = reverse('index')
        return super(ManageAccountView, self).form_valid(form)


class ManageUserGroupsView(SubscriberMixin, AlertTemplateView):
    template_name = "AlertSubscriber/manageUserTopics.html"

    def get_context_data(self, **kwargs):
        context = super(ManageUserGroupsView, self).get_context_data()
        subscriber = Subscriber.objects.get(hash=self.request.session['source_id'])
        subscriptions = TopicSubscription.objects.filter(subscriber=subscriber)
        topics = []
        for i, sub in enumerate(subscriptions):
            topics.append({'topic_name': sub.topic.topic_name, 'topic_arn': sub.topic.topic_arn,
                            'topic_type': sub.topic.topic_type, 'description': sub.topic.description,
                            'id': sub.topic_id, 'subscription_arn' : sub.subscription_arn })
            if sub.status == "active":
                topics[i]['is_subscribed'] = True
            else:
                topics[i]['is_subscribed'] = False
        context['topics'] = topics
        return context


class EditCellPhoneView(SubscriberMixin, View):

    def post(self, request):
        number = re.sub("[()-]", '', self.request.POST['new_number'])
        user_hash = self.request.session['source_id']
        res = change_cell_number(user_hash, number)
        if res != 0:
            pass
            # TODO add error information
        return redirect('manageAccount')


class SubscribeView(SubscriberMixin, View):

    def post(self, request):
        subscriber = Subscriber.objects.get(hash=self.request.session['source_id'])
        topic = Topic.objects.get(id=self.request.POST['id'])
        mysettings = Setting.objects.all()[0]
        amz = AmazonMessage(mysettings.aws_security_key, mysettings.aws_secret_key)
        subscription_arn = amz.subscribe(subscriber.cell_phone, topic.topic_arn)
        if subscription_arn != 0:
            if TopicSubscription.objects.filter(subscriber=subscriber, topic=topic).exists():
                subscription = TopicSubscription.objects.get(subscriber=subscriber, topic=topic)
            else:
                subscription = TopicSubscription()
                subscription.subscriber = subscriber
                subscription.topic = topic
            subscription.subscription_arn = subscription_arn
            subscription.status = 'active'
            subscription.save()
        return redirect('manageUserGroups')


class UnsubscribeView(SubscriberMixin, View):

    def post(self, request):
        subscriber = Subscriber.objects.get(hash=self.request.session['source_id'])
        topic = Topic.objects.get(id=self.request.POST['id'])
        mysettings = Setting.objects.all()[0]
        amz = AmazonMessage(mysettings.aws_security_key, mysettings.aws_secret_key)
        res = amz.unsubscribe(self.request.POST['subscription_arn'])
        if res == 0:
            subscription = TopicSubscription.objects.get(subscriber=subscriber, topic=topic)
            subscription.subscription_arn = 'NA'
            subscription.status = 'disabled'
            subscription.save()
        return redirect('manageUserGroups')


class AlertLogsView(SubscriberMixin, AlertTemplateView):
    template_name = 'AlertSubscriber/messageLog.html'

    def get_context_data(self, **kwargs):
        context = super(AlertLogsView, self).get_context_data(**kwargs)
        subs = TopicSubscription.objects.filter(subscriber=Subscriber.objects.get(hash=self.request.session['source_id']), status="active")
        logs = []
        for sub in subs:
            if MessageLog.objects.filter(topic_name=sub.topic.topic_arn).exists():
                messages = MessageLog.objects.filter(topic_name=sub.topic.topic_arn)
                for message in messages:
                    logs.append({'timestamp': message.timestamp, 'message': message.message,
                                 'topic_name': message.topic_name.split(':')[5], 'initiator': message.initiator})

        context['log_entries'] = logs
        return context


class SendMessageView(GroupRequiredMixin, AlertFormView):
    template_name = 'AlertSubscriber/sendAlert.html'
    group_required = 'instructor'
    form_class = MyMessageForm
    raise_exception = True

    def get_context_data(self):
        context = super(SendMessageView, self).get_context_data()
        context['topics'] = Topic.objects.filter(topic_owner=self.request.user)
        return context

