from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from lti.contrib.django import DjangoToolProvider

from LTI.validator import MyRequestValidator
from CampusClaxon.settings import LTI


class LtiLaunch(View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(LtiLaunch, self).dispatch(request, *args, **kwargs)

    def is_lti_valid(self, request):
        key = LTI['key']
        secret = LTI['secret']
        launch_url = LTI['launch_url']
        tool_provider = DjangoToolProvider(key, secret, request.POST, launch_url) # maybe request.POST instead
        validator = MyRequestValidator()
        valid = tool_provider.is_valid_request(validator)
        if valid: return tool_provider
        else: return None

    @staticmethod
    def is_instructor(tp):
        params = tp.to_params()
        if 'Instructor' in params['roles']: return True
        return False

    @staticmethod
    def is_student(tp):
        params = tp.to_params()
        if 'Learner' in params['roles']: return True
        return False

    @staticmethod
    def get_or_add_user(tp):
        params = tp.to_params()
        email = params['lis_person_contact_email_primary']
        first_name = params['lis_person_name_given']
        last_name = params['lis_person_name_family']
        username = params['ext_user_username']

        if username is None:
            raise "No LTI username provided"
        if email is None:
            email = "{0}@wosc.edu".format(username)

        lti_username = username  #will not work for multiple LMSes
        try:
            user = User.objects.get(username=lti_username)

        except User.DoesNotExist:
            print('creating a new user')
            email = email.rstrip('\x0e')
            user = User.objects.create_user(lti_username, email)
            user.set_unusable_password()

            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name

        except User.MultipleObjectsReturned:
            user = get_object_or_404(User, username=lti_username)

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        # If you want to add them to a special group, here is the pace to do it.
        user_group = Group.objects.get(name='subscriber')
        user.groups.add(user_group)
        user.save()
        return user
