from braces.views import GroupRequiredMixin
from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View
from LTI.lti import LtiLaunch


# This is an example of Single Sign on LTI style with view by view protection.


class Launch(LtiLaunch):

    def post(self, request, *args, **kwargs):
        tp = self.is_lti_valid(request)
        if tp is not None:
            if self.is_instructor(tp):
                user = self.get_or_add_user(tp)
                login(request, user)
                return redirect("indexview")
            if self.is_student(tp):
                return HttpResponse("Student VALID")
            else:
                return redirect("indexview")
        else:
            return HttpResponse("INVALID")


class IndexView(GroupRequiredMixin, View):
    # The GroupRequiredMixin is needed to protect the views based on group
    group_required = "editor"
    raise_exception = True

    def get(self, request, *args, **kwargs):
        response = "<h1>TADA</h1>"
        return HttpResponse(response)



