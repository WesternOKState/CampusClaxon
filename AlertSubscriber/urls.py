"""CampusClaxon URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from .views import IndexView, ManageAccountView, ManageUserGroupsView, AlertLogsView, EditCellPhoneView, SubscribeView, \
    UnsubscribeView, SendMessageView

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^$', IndexView.as_view(), name="index"),
    url(r'^manageAccounts/$', ManageAccountView.as_view(), name="manageAccount"),
    url(r'^manageTopics/$', ManageUserGroupsView.as_view(), name="manageUserGroups"),
    url(r'^viewLogs/$', AlertLogsView.as_view(), name="viewLogs"),
    url(r'^editSubscriberCellPhone/$', EditCellPhoneView.as_view(),
        name="edit_subscriber_cell_phone"),
    url(r'^subscribe/$', SubscribeView.as_view(), name="subscribe"),
    url(r'^unsubscribe/$', UnsubscribeView.as_view(), name="unsubscribe"),
    url(r'^sendMessage/$', SendMessageView.as_view(), name="send_message"),
]
