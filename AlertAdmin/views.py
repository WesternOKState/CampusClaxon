import datetime
import re
import os
import simplejson as json
from braces.views import GroupRequiredMixin, LoginRequiredMixin
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import RedirectView
from django.views.generic import View

from LTI.lti import LtiLaunch
from CampusClaxon.AmazonMessage import AmazonMessage
from CampusClaxon.lib import get_hash, processFile, change_cell_number, AlertTemplateView, AlertFormView, AlertListView
from .forms import MyMessageForm, SettingsForm, TemplateForm, TopicForm, SubscriberForm, FileUploadForm, \
    AddSubscriberForm, NewTopicForm
from .models import MessageLog, Topic, Setting, Template, Subscriber, TopicSubscription

class IndexView(GroupRequiredMixin,AlertTemplateView):
    group_required = "admin"
    template_name = "AlertAdmin/index.html"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data()
        context['number_of_topics'] = Topic.objects.all().count()
        context['number_of_subscribers'] = Subscriber.objects.all().count()
        context['number_of_templates'] = Template.objects.all().count()
        return context


class SendAlertView(GroupRequiredMixin, AlertFormView):
    group_required = "admin"
    form_class = MyMessageForm
    template_name = 'AlertAdmin/sendAlert.html'
    raise_exception = True

    def get_context_data(self, **kwargs):
        my_template = None
        my_topic = None
        selected_arn = None
        if 'template' in self.request.GET:
            my_template = self.request.GET['template']
        elif 'topic' in self.request.GET:
            my_topic = self.request.GET['topic']

        context = super(SendAlertView, self).get_context_data(**kwargs)
        templates = Template.objects.all().values()
        if my_template is not None:
            for i, template in enumerate(templates):
                if int(template['id']) == int(my_template):
                    templates[i]['selected'] = "True"
                    selected_arn = Topic.objects.get(id=template['topic_id']).topic_arn
                    context['message'] = template['default_message']
                else:
                    templates[i]['selected'] = "False"
            topics = Topic.objects.all().values()
            if selected_arn is not None:
                for i, topic in enumerate(topics):
                    if topic['topic_arn'] == selected_arn:
                        topics[i]['selected'] = "True"
                        context['display_name'] = topic['display_name'] + ">"
                    else:
                        topics[i]['selected'] = "False"
        elif my_topic is not None:
            topics = Topic.objects.all().values()
            if my_topic is not None:
                for i, topic in enumerate(topics):
                    print(topic['id'])
                    if int(topic['id']) == int(my_topic):
                        topics[i]['selected'] = "True"
                        context['display_name'] = topic['display_name'] + ">"
                    else:
                        topics[i]['selected'] = "False"
        else:
            topics = Topic.objects.all().values()
            templates = Template.objects.all().values()

        context['topics'] = topics
        context['templates'] = templates
        return context

    def form_valid(self, form):
        my_settings = Setting.objects.all()[0]
        message_log = MessageLog()
        message_log.initiator = self.request.user
        message_log.topic_name = self.request.POST['topic']
        message_log.message = self.request.POST['message']
        message_log.timestamp = datetime.datetime.now()
        message_log.save()
        message_sender = AmazonMessage(my_settings.aws_security_key, my_settings.aws_secret_key,)
        message_sender.send_message(self.request.POST['message'], self.request.POST['topic'])
        self.success_url = reverse('index2')
        return super(SendAlertView, self).form_valid(form)


class ViewLogs(GroupRequiredMixin, AlertListView):
    group_required = "admin"
    template_name = 'AlertAdmin/messageLog.html'
    context_object_name = 'log_entries'
    raise_exception = True

    def get_queryset(self):
        return MessageLog.objects.all()


class EditSettingsView(GroupRequiredMixin, AlertFormView):
    group_required = "admin"
    template_name = "AlertAdmin/editSettings.html"
    form_class = SettingsForm
    success_url = "/"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(EditSettingsView, self).get_context_data()
        if Setting.objects.all().count() > 0:
            theme = Setting.objects.all()[0].theme_name
        else:
            theme = ''
        themes = []
        res = os.listdir('templates/theme/')
        for r in res:
            t = {}
            if r == theme:
                t['selected'] ="True"
            else:
                t['selected'] = "False"
            t['name'] = r
            themes.append(t)
        context['themes'] = themes
        return context

    def get_initial(self):
        if Setting.objects.all().count() > 0:
            mySettings = Setting.objects.all()[0]
            return {'aws_security_key': mySettings.aws_security_key,
                    'aws_secret_key': mySettings.aws_secret_key,
                    'theme_name': mySettings.theme_name}

    def form_valid(self, form):
        mySettings = Setting(pk=1)
        mySettings.aws_security_key = self.request.POST['aws_security_key']
        mySettings.aws_secret_key = self.request.POST['aws_secret_key']
        mySettings.theme_name = self.request.POST['theme_name']
        mySettings.authentication_type = self.request.POST['authentication_type']
        mySettings.save()
        return super(EditSettingsView, self).form_valid(form)


class ManageTemplates(GroupRequiredMixin, AlertListView):
    group_required = "admin"
    template_name = 'AlertAdmin/manageTemplates.html'
    context_object_name = 'templates'
    raise_exception = True

    def get_queryset(self):
        return Template.objects.all()


class EditTemplateView(GroupRequiredMixin, AlertFormView):
    group_required = "admin"
    raise_exception = True
    form_class = TemplateForm
    template_name = 'AlertAdmin/editTemplate.html'


    def get_initial(self):
        template = Template.objects.get(pk=self.kwargs['pk'])
        return {'template_name': template.template_name,
                'default_message': template.default_message}

    def get_context_data(self, **kwargs):
        context = super(EditTemplateView, self).get_context_data()
        topics = Topic.objects.all().values()
        for i,topic in enumerate(topics):
            if topic['id'] == Template.objects.get(id=self.kwargs['pk']).topic_id:
                topics[i]['selected'] = True
            else:
                topics[i]['selected'] = False
        context['topics'] = topics
        return context

    def form_valid(self, form):
        myTemplate = Template.objects.get(pk=self.kwargs['pk'])
        myTemplate.template_name = self.request.POST['template_name']
        myTemplate.default_message = self.request.POST['default_message']
        myTemplate.topic = Topic.objects.get(pk=self.request.POST['topic'])
        myTemplate.save()
        self.success_url = reverse('manageTemplates')
        return super(EditTemplateView, self).form_valid(form)


class NewTemplateView(GroupRequiredMixin, AlertFormView):
    group_required = "admin"
    raise_exception = True
    form_class = TemplateForm
    template_name = 'AlertAdmin/newTemplate.html'
    success_url = "/manageTemplates"

    def get_context_data(self, **kwargs):
        context = super(NewTemplateView, self).get_context_data(**kwargs)
        mysettings = Setting.objects.get(pk=1)
        amz = AmazonMessage(mysettings.aws_security_key, mysettings.aws_secret_key)
        context['topics'] = Topic.objects.all()
        return context

    def form_valid(self, form):
        myTemplate = Template()
        myTemplate.template_name = self.request.POST['template_name']
        myTemplate.default_message = self.request.POST['default_message']
        myTemplate.topic = Topic.objects.get(id=self.request.POST['topic_name'])
        myTemplate.save()
        return super(NewTemplateView, self).form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super(NewTemplateView, self).form_invalid(form)


class SuccessView(AlertTemplateView):
    template_name = "AlertAdmin/success.html"

    def get_context_data(self, **kwargs):
        context = super(SuccessView, self).get_context_data(**kwargs)
        try:
            context['location'] = self.kwargs['location']
            if 'location2' in self.kwargs:
                context['location'] += '/' + self.kwargs['location2'] + '/'
        except:
            pass
        return context


class ManageTopics(GroupRequiredMixin, AlertTemplateView):
    group_required = "admin"
    template_name = 'AlertAdmin/manageTopics.html'
    context_object_name = 'topics'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(ManageTopics, self).get_context_data(**kwargs)
        context['topics'] = Topic.objects.all()
        return context


class BrowseTopicSubscriberView(GroupRequiredMixin, AlertTemplateView):
    group_required = "admin"
    template_name = "AlertAdmin/browseTopicSubscribers.html"

    def get_context_data(self, **kwargs):
        context = super(BrowseTopicSubscriberView, self).get_context_data(**kwargs)
        subscriptions = TopicSubscription.objects.filter(topic=Topic.objects.get(topic_arn=self.kwargs['topic']), status='active')

        subscribers = []
        for sub in subscriptions:
            person = { 'last_name': sub.subscriber.last_name, 'first_name' : sub.subscriber.first_name ,
                       'cell_phone': sub.subscriber.cell_phone, 'student_id' : sub.subscriber.student_id,
                       'SubscriptionArn': sub.topic, 'hash': sub.subscriber.hash}
            subscribers.append(person)
        context['subscribers'] = subscribers
        tn = self.kwargs['topic'].split(':')[5]
        context['topic'] = {'arn': self.kwargs['topic'], 'name': tn }
        return context


class RemoveSubscriberView(GroupRequiredMixin, RedirectView):
        group_required = "admin"

        def post(self, *args, **kwargs):
            mysettings = Setting.objects.get(pk=1)
            amz = AmazonMessage(mysettings.aws_security_key, mysettings.aws_secret_key)
            res = amz.unsubscribe(self.request.POST['SubscriptionArn'])
            if res == 0:
                sub = TopicSubscription.objects.get(subscription_arn=self.request.POST['SubscriptionArn'])
                sub.delete()
                if 'referer' in self.request.POST:
                    return HttpResponseRedirect(reverse('editSubscriber', kwargs={'hash':self.request.POST['hash']}))
                return redirect('editSubscriber', self.request.POST['hash'])
            else:
                #TODO: Error Informmation in case of an issue removing subscriptioon from AWS
                return redirect('editSubscriber', self.request.POST['hash'])


class RemoveAccountView(GroupRequiredMixin, RedirectView):
    group_required = "admin"

    def post(self, *args, **kwargs):

        mysettings = Setting.objects.get(pk=1)
        amz = AmazonMessage(mysettings.aws_security_key, mysettings.aws_secret_key)
        subscriber = Subscriber.objects.get(hash=self.request.POST['hash'])
        subscriptions = TopicSubscription.objects.filter(subscriber=subscriber)
        for sub in subscriptions:
            res = amz.unsubscribe(sub.subscription_arn)
            if res != 0:
                # TODO Error Message
                return redirect('manageSubscribers')
            sub.delete()
        subscriber.delete()
        return redirect('manageSubscribers')


class NewTopicView(GroupRequiredMixin, AlertFormView):
    group_required = "admin"
    raise_exception = True
    form_class = NewTopicForm
    template_name = 'AlertAdmin/newTopic.html'
    success_url = "/manageGroups"

    def form_valid(self, form):
        mysettings = Setting.objects.get(pk=1)
        amz = AmazonMessage(mysettings.aws_security_key, mysettings.aws_secret_key)
        res = amz.create_topic(self.request.POST['topic_name'])
        if res != 0:
            amz.set_topic_attributes(res, self.request.POST['display_name'])
            myTopic = Topic()
            myTopic.topic_name = self.request.POST['topic_name']
            myTopic.topic_arn = res
            myTopic.topic_owner = User.objects.get(pk=self.request.POST['topic_owner'])
            myTopic.description = self.request.POST['description']
            myTopic.topic_type = self.request.POST['type']
            myTopic.display_name = self.request.POST['display_name']
            myTopic.save()

            mysettings = Setting.objects.get(pk=1)
            amz = AmazonMessage(mysettings.aws_security_key, mysettings.aws_secret_key)

            if myTopic.topic_type == 'public':
                subscribers = Subscriber.objects.all()
                for sub in subscribers:
                    if not TopicSubscription.objects.filter(subscriber=sub, topic=myTopic).exists():
                        newSubscription = TopicSubscription()
                        newSubscription.subscriber = sub
                        newSubscription.subscription_arn = 'NA'
                        newSubscription.topic = myTopic
                        newSubscription.status = 'disabled'
                        newSubscription.save()

            if myTopic.topic_type == 'required':
                subscribers = Subscriber.objects.all()
                for sub in subscribers:
                    res = amz.subscribe(sub.cell_phone, myTopic.topic_arn)
                    if res != 0:
                        print("Subscribed " + sub.last_name)
                        if TopicSubscription.objects.filter(subscriber=sub, topic=myTopic).exists():
                            newSubscription = TopicSubscription.objects.get(subscriber=sub, topic=myTopic)
                        else:
                            newSubscription = TopicSubscription()
                            newSubscription.subscriber = sub
                            newSubscription.topic = myTopic

                        newSubscription.subscription_arn = res
                        newSubscription.status = 'active'
                        newSubscription.save()

        return super(NewTopicView, self).form_valid(form)


class RemoveTopicView(GroupRequiredMixin, RedirectView):
    group_required = "admin"
    # template_name = get_template('success.html')

    def get(self, *args, **kwargs):
        mysettings = Setting.objects.get(pk=1)
        amz = AmazonMessage(mysettings.aws_security_key, mysettings.aws_secret_key)
        res = amz.delete_topic(self.kwargs['topic'])
        if res == 0:
            topic = Topic.objects.get(topic_arn=self.kwargs['topic'])
            topic.delete()
            return redirect('manageTopics')
        else:
            # TODO Add Error Message
            return redirect('manageTopics')


class EditTopicView(GroupRequiredMixin, AlertFormView):
    group_required = "admin"
    raise_exception = True
    form_class = TopicForm
    template_name = 'AlertAdmin/editTopic.html'
    success_url = "/success/manageGroups"

    def get_initial(self):
        topic = Topic.objects.get(pk=self.kwargs['pk'])
        return {'topic_name': topic.topic_name,
                'topic_owner': topic.topic_owner,
                'display_name': topic.display_name}

    def get_context_data(self, **kwargs):
        context = super(EditTopicView, self).get_context_data()
        context['topic_arn'] = Topic.objects.get(pk=self.kwargs['pk']).topic_arn
        return context

    def form_valid(self, form):
        mysettings = Setting.objects.get(pk=1)
        amz = AmazonMessage(mysettings.aws_security_key, mysettings.aws_secret_key)
        res = amz.set_topic_attributes(self.request.POST['topic_arn'], self.request.POST['display_name'])
        if res == 0:
            myTopic = Topic.objects.get(pk=self.kwargs['pk'])
            myTopic.topic_owner = User.objects.get(pk=self.request.POST['topic_owner'])
            myTopic.save()
        else:
            # TODO Display Error
            pass
        return super(EditTopicView, self).form_valid(form)


class EditSubscriberView(GroupRequiredMixin, AlertFormView):
    group_required = "admin"
    raise_exception = True
    form_class = SubscriberForm
    template_name = "AlertAdmin/editSubscriber.html"

    def get_context_data(self, **kwargs):
        context = super(EditSubscriberView, self).get_context_data(**kwargs)
        subscriber = Subscriber.objects.get(hash=self.kwargs['hash'])
        context['subscriber'] = subscriber
        context['topics'] = []
        subscriptions = TopicSubscription.objects.filter(subscriber=subscriber)
        context['authentication_type'] = Setting.objects.all()[0].authentication_type
        for sub in subscriptions:
            topic = sub.topic
            myTop = {'topic_name': topic.topic_name, 'topic_arn': topic.topic_arn, 'subscription_arn': sub.subscription_arn}
            context['topics'].append(myTop)
        print(context['topics'])
        return context

    def get_initial(self):
        subscriber = Subscriber.objects.get(hash=self.kwargs['hash'])
        return {'last_name':subscriber.last_name,
                'first_name':subscriber.first_name,
                'cell_phone': subscriber.cell_phone,
                'student_id': subscriber.student_id,
                'personal_email': subscriber.personal_email,
                'school_email': subscriber.school_email,
                'hash': self.kwargs['hash']}

    def form_valid(self, form):
        subscriber = Subscriber.objects.get(hash=self.request.POST['hash'])
        subscriber.first_name = self.request.POST['first_name']
        subscriber.last_name = self.request.POST['last_name']
        subscriber.student_id = self.request.POST['student_id']
        subscriber.personal_email = self.request.POST['personal_email']
        subscriber.school_email = self.request.POST['school_email']
        subscriber.save()
        if Setting.objects.all()[0].authentication_type == 'internal':
            user = User.objects.get(email=self.request.POST['school_email'])
            if self.request.POST['password'] != '':
                user.set_password(self.request.POST['password'])
            user.save()
        self.success_url = reverse('manageSubscribers')
        return super(EditSubscriberView, self).form_valid(form)


class EditCellPhoneView(GroupRequiredMixin, View):
    group_required = "admin"

    def get_context_data(self):
        context = super(EditCellPhoneView, self).get_context_data()
        context['old_number'] = re.sub("[()-]", '', self.request.POST['old_number'])
        return context

    def post(self, form):
        number = re.sub("[()-]", '', self.request.POST['new_number'])
        user_hash = self.request.session['source_id']
        res = change_cell_number(user_hash, number)
        if res != 0:
            print(res)
        #TODO add error information
        return redirect('editSubscriber', self.request.POST['hash'])


class ManageTopicSubscribersView(AlertTemplateView):
    group_required = "admin"
    template_name = "AlertAdmin/manageTopicSubscribers.html"
    raise_exception = True


    def get_context_data(self, **kwargs):
        context = super(ManageTopicSubscribersView, self).get_context_data(**kwargs)
        name = self.kwargs['topic'].split(':')[5]
        context['topic'] = {'name': name, 'arn': self.kwargs['topic']}
        return context


class UploadSubscribersView(GroupRequiredMixin, AlertFormView):
    group_required = "admin"
    template_name = "AlertAdmin/bulkUpload.html"
    form_class = FileUploadForm
    raise_exception = True
    success_url = "/success/ManageTopicSubscribers"

    def get_context_data(self, **kwargs):
        context = super(UploadSubscribersView, self).get_context_data(**kwargs)
        context['topic'] = {'arn': self.kwargs['topic']}
        return context

    def form_valid(self, form):
        myFile = self.request.FILES['import_file']
        processFile(myFile, self.kwargs['topic'])
        return super(UploadSubscribersView, self).form_valid(form)


class NewSubscriberView(GroupRequiredMixin, AlertFormView):
    group_required = "admin"
    raise_exception = True
    form_class = AddSubscriberForm
    template_name = 'AlertAdmin/newSubscriber.html'

    def get_context_data(self, **kwargs):
        context = super(NewSubscriberView, self).get_context_data(**kwargs)
        context['authentication_type'] = Setting.objects.all()[0].authentication_type
        if 'topic' in self.kwargs: context['topic'] = self.kwargs['topic']
        return context

    def form_valid(self, form):
        number = re.sub("[()-]", '', form['cell_phone'].value())
        if Subscriber.objects.filter(cell_phone=number).exists():
            # If user Currently Exists, and does not have an active subscription to the current topic
            mySubscriber = Subscriber.objects.get(cell_phone=number)
            if not TopicSubscription.objects.filter(topic=Topic.objects.get(topic_arn=self.kwargs['topic']),
                                                    subscriber=mySubscriber, status='active').exists():
                if 'topic' in self.kwargs:
                    self.subscribe_to_current(mySubscriber)
                self.success_url = "/success/browseTopicSubscribers/" + self.request.POST['topic'] + '/'
                return super(NewSubscriberView, self).form_valid(form)
        else:
            # User dies not exist, so add them to required, add inactive to public(s) and add them to the current.
            mySubscriber = Subscriber()
            mySubscriber.first_name = self.request.POST['first_name']
            mySubscriber.last_name = self.request.POST['last_name']
            mySubscriber.cell_phone = number
            mySubscriber.student_id = self.request.POST['student_id']
            mySubscriber.personal_email = self.request.POST['personal_email']
            mySubscriber.school_email = self.request.POST['school_email']
            mySubscriber.save()

            if Setting.objects.all()[0].authentication_type == 'internal':
                user = User.objects.create_user(self.request.POST['school_email'],
                                                email=self.request.POST['school_email'],
                                                password=self.request.POST['password'],
                                                first_name = self.request.POST['first_name'],
                                                last_name = self.request.POST['last_name']
                                                )
                user.groups.add(Group.objects.get(name='subscriber'))
                user.save()
            if 'topic' in self.kwargs:
                self.subscribe_to_public(mySubscriber)

            res = self.subscribe_to_required(mySubscriber)
            if res != 0:
                if 'topic' in self.kwargs:
                    if self.subscribe_to_current(mySubscriber) != 0:
                        self.success_url = "/success/browseTopicSubscribers/" + self.request.POST['topic'] + '/'
                        return super(NewSubscriberView, self).form_valid(form)
                else:
                    self.success_url = reverse("manageSubscribers")
                    return super(NewSubscriberView, self).form_valid(form)
        # If we got this far, something went wrong.
        # TODO: Error page
        self.success_url = "/success/browseTopicSubscribers/" + self.request.POST['topic'] + '/'
        return super(NewSubscriberView, self).form_valid(form)

    def subscribe_to_current(self, subscriber):
        topic = Topic.objects.get(topic_arn=self.kwargs['topic'])
        # if already has a subscription, get it.
        subscription = TopicSubscription()
        if TopicSubscription.objects.filter(topic=topic, subscriber=subscriber).exists():
            subscription = TopicSubscription.objects.get(topic=topic, subscriber=subscriber)

        # if it is not an active subscription, activate it.

        if subscription.status != 'active':
            mysettings = Setting.objects.get(pk=1)
            amz = AmazonMessage(mysettings.aws_security_key, mysettings.aws_secret_key)
            res = amz.subscribe(subscriber.cell_phone, topic.topic_arn)
            if res != 0:
                subscription.subscriber = subscriber
                subscription.topic = topic
                subscription.status = 'active'
                subscription.subscription_arn = res
                subscription.save()
            return res
        else:
            return subscription.subscription_arn

    def subscribe_to_required(self, subscriber):
        topics = Topic.objects.filter(topic_type="required")
        for topic in topics:
            if not TopicSubscription.objects.filter(topic=topic, subscriber=subscriber).exists():
                mysettings = Setting.objects.get(pk=1)
                amz = AmazonMessage(mysettings.aws_security_key, mysettings.aws_secret_key)
                res = amz.subscribe(subscriber.cell_phone, topic.topic_arn)
                print("Required: " + res)
                if res != 0:
                    subscription = TopicSubscription()
                    subscription.subscriber = subscriber
                    subscription.topic = topic
                    subscription.status = 'active'
                    subscription.subscription_arn = res
                    subscription.save()
                    return res
                else:
                    return 0

    def subscribe_to_public(self, subscriber):
        topics = Topic.objects.filter(topic_type="public")
        for topic in topics:
            if not TopicSubscription.objects.filter(topic=topic, subscriber=subscriber).exists():
                subscription = TopicSubscription()
                subscription.subscriber = subscriber
                subscription.topic = topic
                subscription.status = 'disabled'
                subscription.subscription_arn = 'NA'
                subscription.save()
        return 0

    def form_invalid(self, form):
        print(form.errors)


class syncSubscribersView(GroupRequiredMixin, RedirectView):
    group_required = "admin"
    raise_exception = True
    url = '/success/manageTopicSubscribers'

    def get_redirect_url(self, *args, **kwargs):

        subscribers = Subscriber.objects.filter(account_processed = False)
        mysettings = Setting.objects.get(pk=1)
        topic = Topic.objects.get(topic_name="IT Fulltime")
        #getTopicSubscribers(topic.id)
        amazon = AmazonMessage(mysettings.aws_security_key, mysettings.aws_secret_key)
        topic = amazon.create_topic('New_Topic')
        amazon.subscribe('15803011758', topic)


        # for subscriber in subscribers:
        #     amazon.get_subscriber_arn(mysettings.aws_security_key,
        #                      mysettings.aws_secret_key,
        #                      subscriber.cell_phone,
        #                      topic.topic_arn)

            # subscriber.account_processed = True
            # subscriber.save()

        # sync subscriptions tables
        # topics = Topic.objects.all()
        # for topic in topics:
        #     # This will be a list of cell phone numbers
        #     subscribers = getTopicSubscribers(topic.pk)

        return reverse("Manage Subscribers")


class FindUserView(GroupRequiredMixin, View):
    group_required = "admin"


# todo fix search now that # is formatted.
    def get(self, request):

        response = []
        if Subscriber.objects.filter(cell_phone__contains=self.request.GET['q']).exists():
            subs = Subscriber.objects.filter(cell_phone__contains=self.request.GET['q'])
            for sub in subs:
                info = {}
                info['id'] = sub.id
                info['last_name'] = sub.last_name
                info['first_name'] = sub.first_name
                number = "{}({}){}-{}".format(sub.cell_phone[0], sub.cell_phone[1:4], sub.cell_phone[4:7],
                                              sub.cell_phone[7:])
                info['cell_phone'] = number
                info['student_id'] = sub.student_id
                info['personal_email'] = sub.personal_email
                info['school_email'] = sub.school_email
                response.append(info)
        else:
            response = {}
            response['results'] = '0'
        res = json.dumps(response)
        return HttpResponse(res, content_type='application/json')


class FindUserByNameView(GroupRequiredMixin, View):
    group_required = "admin"

    def get(self, request):

        response = []
        if Subscriber.objects.filter(Q(last_name__istartswith=self.request.GET['q']) | Q(first_name__istartswith=self.request.GET['q'])).exists():
            subs = Subscriber.objects.filter(Q(last_name__istartswith=self.request.GET['q']) | Q(first_name__istartswith=self.request.GET['q']))
            for sub in subs:
                info = {}
                info['id'] = sub.id
                info['last_name'] = sub.last_name
                info['first_name'] = sub.first_name
                number = "{}({}){}-{}".format(sub.cell_phone[0],sub.cell_phone[1:4],sub.cell_phone[4:7],
                                              sub.cell_phone[7:])
                info['cell_phone'] = number
                info['student_id'] = sub.student_id
                info['personal_email'] = sub.personal_email
                info['school_email'] = sub.school_email
                response.append(info)
        else:
            response = {}
            response['results'] = '0'
        res = json.dumps(response)
        return HttpResponse(res, content_type='application/json')


class ManageSubscribersView(GroupRequiredMixin, AlertTemplateView):
    template_name = "AlertAdmin/manageSubscribers.html"
    group_required = 'admin'

    def get_context_data(self, **kwargs):
        context = super(ManageSubscribersView, self).get_context_data(**kwargs)
        context['subscribers'] = Subscriber.objects.all()
        context['total'] = Subscriber.objects.all().count()
        return context

class ImportCourseView(LoginRequiredMixin, AlertTemplateView):
    template_name = "AlertAdmin/loading.html"

    # def get(self):
    #     setting = Setting.objects.all()[0]
    #     amz = AmazonMessage(setting.aws_security_key, setting.aws_secret_key)
    #     res = amz.create_topic(self.request.GET['section'])
    #     if res != 0:
    #         Topic.objects.create(topic_name=self.request.GET['section'], topic_arn=res, topic_type='private',
    #                              description=self.request.GET['course_title'], topic_owner='admin',
    #                              display_name=self.request.GET['course'])
    #         amz.set_topic_attributes(res, self.request.GET['course'])
    #         students = get_lms_students(self.request.GET['section'])
    #
    #         for student in students:
    #             if Subscriber.objects.get(student_id=student).exists():
    #                 subscriber = Subscriber.objects.get(student_id=student)
    #                 topic = Topic.objects.get(topic_name=self.kwargs['section'])
    #                 if not TopicSubscription.objects.filter(subscriber=subscriber,
    #                                                     topic=topic).exists():
    #                     TopicSubscription.objects.create(subscriber=subscriber, topic=topic,
    #                                                      subscription_arn='na', status='disabled')
    #     return redirect('subscribe')

def removeTopic(request, topic_id):
    Topic.objects.get(pk=topic_id).delete()
    return redirect("/success/manageTopics")


def removeTemplate(request, template_id):
    Template.objects.get(pk=template_id).delete()
    return redirect("/success/manageTemplates")


# LTI Views

class Launch(LtiLaunch):

    def post(self, request, *args, **kwargs):
        # Returns tp if valid LTI user
        tp = self.is_lti_valid(request)
        if tp is not None:
            # Get the user or add them if tehy do not currently exist
            user = self.get_or_add_user(tp)
            params = tp.to_params()

            # get the course number from the course title if this is a Moodle integration

            m = re.search("\[[(a-zA-Z0-9)]+\]", params['context_title'])
            course_num = None
            if m:
                course_num = m.group(0)[1:len(m.group(0)) - 1]

            self.request.session['source_id'] = get_hash(params['lis_person_sourcedid'])
            if self.is_instructor(tp):
                login(request, user)

                # if we got here from a course and a topic for the course has not been setup, set it up
                if not Topic.objects.filter(topic_name=params['context_label']).exists() and course_num is not None:
                    # Install the topic
                    return redirect(reverse('import_course') + "?section={}&course={}".format(params['context_label'],
                                                                                             course_num))

                if user.groups.filter(name='admin').exists():
                    # If the user is in the admin group, send them to the admin page.
                    return redirect("adminIndex")

                return redirect("index")

            if self.is_student(tp):
                login(request, user)
                # if we got here from a course and the topic has not been setup, set it up.
                if not Topic.objects.filter(topic_name=params['context_label']).exists()  and course_num is not None:
                    return redirect(
                        reverse('import_course') + "?section={}&course={}".format(params['context_label'], course_num))
                return redirect("index")
            else:
                return HttpResponse("You must be an instructor or student.")
        else:
            return HttpResponse("INVALID")

