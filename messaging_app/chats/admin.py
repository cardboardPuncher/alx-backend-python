from django.contrib import admin
from chats.models import Conversation, User, Message
# Register your models here.

admin.site.register(Conversation)
admin.site.register(User)
admin.site.register(Message)