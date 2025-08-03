from django.contrib import admin
from messaging.models import Conversation, User, Message, Notification
# Register your models here.

admin.site.register(Conversation)
admin.site.register(User)
admin.site.register(Message)
admin.site.register(Notification)