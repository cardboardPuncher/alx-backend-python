from django.db import models

class MessageRepliesManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().select_related("replies")
    
class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user) -> models.QuerySet:
        return super().get_queryset().filter(receiver=user, read=False)