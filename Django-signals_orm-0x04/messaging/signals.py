from django.db.models.signals import post_save, post_delete, pre_save
from messaging.models import Message, Notification, MessageHistory
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from datetime import datetime

@receiver(post_save, sender=Message)
def notification_creator(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message = instance
        )

@receiver(pre_save, sender=Message)
def log_old_messages(sender, instance, **kwargs):
    if instance.pk is not None:
        old = Message.objects.filter(pk=instance.pk).first()
        if old and old.content != instance.content:
            instance.edited = True
            instance.edited_at = datetime.now()
            instance.edited_by = instance.sender
            MessageHistory.objects.create(
                message=old,
                old_content=old.content
            )


@receiver(post_delete, sender=get_user_model())
def on_user_deleted(sender, instance, **kwargs):
    MessageHistory.objects.filter(message__sender=instance).delete()
    Message.objects.filter(sender=instance).delete()
    Notification.objects.filter(user=instance).delete()