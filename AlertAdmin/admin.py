from django.contrib import admin
from .models import MessageLog, Setting, Topic, Template,Subscriber, TopicSubscription, ResultsLog
from django.contrib.sessions.models import Session


class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()
    list_display = ['session_key', '_session_data', 'expire_date']

class SubscriberAdmin(admin.ModelAdmin):
    search_fields = ['cell_phone', 'last_name', 'first_name']
    list_display = ['last_name', 'first_name', 'student_id', 'cell_phone']

class ResultsLogAdmin(admin.ModelAdmin):
    list_display = ['to', 'status', 'client_ref']

# Register your models here.
admin.site.register(MessageLog)
admin.site.register(ResultsLog, ResultsLogAdmin)
admin.site.register(Setting)
admin.site.register(Topic)
admin.site.register(Template)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(TopicSubscription)
admin.site.register(Session)