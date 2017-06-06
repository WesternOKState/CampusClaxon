from django.conf.urls import url, include
from .views import IndexView, SendAlertView, ViewLogs, \
    EditSettingsView, ManageTemplates, EditTemplateView, NewTemplateView, SuccessView, removeTemplate, ManageTopics, \
    NewTopicView, EditTopicView, ManageTopicSubscribersView, NewSubscriberView, UploadSubscribersView, \
    EditSubscriberView, SyncSubscribersView, Launch, RemoveTopicView, \
    RemoveSubscriberView, FindUserView, FindUserByNameView, EditCellPhoneView, ManageSubscribersView, \
    BrowseTopicSubscriberView, RemoveAccountView, ImportCourseView, QuickAlertView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name="adminIndex"),
    url(r'^launch/', Launch.as_view(), name='launch'),
    url(r'^index/$', IndexView.as_view(), name="index2"),
    url(r'^manageGroups/$', ManageTopics.as_view(), name="manageTopics"),
    url(r'^manageSubscribers/$', ManageSubscribersView.as_view(), name="manageSubscribers"),
    url(r'^manageTemplates/$', ManageTemplates.as_view(), name="manageTemplates"),
    url(r'^alert/sendAlert/$', SendAlertView.as_view(), name="Send Alert"),
    url(r'^alert/sendAlert/(?P<pk>[0-9]+)/$', SendAlertView.as_view(), name="Send Alert2"),
    url(r'^alert/viewLogs/$', ViewLogs.as_view(), name="alert"),
    url(r'^alert/editSettings/$', EditSettingsView.as_view(), name="editAlertSettings"),
    url(r'^editSettings/$', EditSettingsView.as_view(), name="editSettings"),
    url(r'^editTemplate/(?P<pk>[0-9]+)/$', EditTemplateView.as_view(), name="editTemplate"),
    url(r'^removeTemplate/(?P<template_id>[0-9]+)/$', removeTemplate, name="removeTemplate"),
    url(r'^newTemplate/$', NewTemplateView.as_view(), name="newTemplate"),
    url(r'^newTopic/$', NewTopicView.as_view(), name="newTopic"),
    url(r'^removeTopic/(?P<topic>[:\-a-zA-Z0-9_]+)/$', RemoveTopicView.as_view(), name="removeTopic"),
    url(r'^editTopic/(?P<pk>[0-9]+)/$', EditTopicView.as_view(), name="editTopic"),
    url(r'^manageTopicSubscribers/(?P<topic>[:\-a-zA-Z0-9_]+)/$', ManageTopicSubscribersView.as_view(),
        name="manageTopicSubscribers"),
    url(r'^addSubscriber/(?P<topic>[:\-a-zA-Z0-9_]+)/$', NewSubscriberView.as_view(), name="addSubscribers"),
    url(r'^addSubscriber/$', NewSubscriberView.as_view(), name="addSubscribers"),
    url(r'^uploadSubscriber/(?P<topic>[:\-a-zA-Z0-9_]+)/$', UploadSubscribersView.as_view(), name="uploadSubscribers"),
    url(r'^success/(?P<location>[A-Za-z]+)/(?P<location2>[:\-a-zA-Z0-9_]+)/$', SuccessView.as_view(), name="Success"),
    url(r'^success/(?P<location>[A-Za-z]+)/$', SuccessView.as_view(), name="Success"),
    url(r'^success/$', SuccessView.as_view(), name="Success"),
    url(r'^browseTopicSubscribers/?page=(?P<page>[0-9]+)/$', BrowseTopicSubscriberView.as_view(), name="browseSubscribers"),
    url(r'^browseTopicSubscribers/(?P<topic>[:\-a-zA-Z0-9_]+)/$', BrowseTopicSubscriberView.as_view(),
        name="browseSubscribers"),
    url(r'^editSubscriber/(?P<hash>[a-f0-9]+)/$', EditSubscriberView.as_view(), name="editSubscriber"),
    url(r'^editCellPhone/$', EditCellPhoneView.as_view(), name="edit_cell_phone"),
    url(r'^removeSubscriber/$', RemoveSubscriberView.as_view(), name="removeSubscriber"),
    url(r'^syncSubscribers/$', SyncSubscribersView.as_view(), name="Sync"),
    url(r'^findUser/$', FindUserView.as_view(), name="find_user"),
    url(r'^findUserByName/$', FindUserByNameView.as_view(), name="find_user_by_name"),
    url(r'^subscriber/', include('AlertSubscriber.urls')),
    url(r'^removeAccount/(?P<hash>[a-f0-9]+)/$', RemoveAccountView.as_view(), name="removeAccount"),
    url(r'^importClass/$', ImportCourseView.as_view(), name='import_course'),
    url(r'^quickalert/', QuickAlertView.as_view(), name="quickalert"),
]