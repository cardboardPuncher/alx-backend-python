from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.urls import reverse

# Create your models here.
class User(AbstractUser):

    class UserRole(models.TextChoices):
        HOST = "HST", _("Host")
        ADMIN = "ADN", _("Administrator")
        GUEST = "GST", _("Guest")

    user_id = models.UUIDField(
        verbose_name='User ID',
        default= uuid.uuid4,
        primary_key= True,
        editable=False
        )
    
    first_name = models.CharField(
        verbose_name= 'First Name',
        max_length= 70,
        null= False
    )
    last_name = models.CharField(
        verbose_name= 'Last Name',
        max_length= 100,
        null= False 
    )
    email = models.EmailField(
        verbose_name='Email of User',
        unique=True,
        null= False
    )
    role = models.CharField(
        verbose_name= 'Role of the user',
        choices= UserRole.choices,
        null= False,
        default=UserRole.GUEST
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True
    )


    class Meta:
        ordering = ['-created_at']
        

    def __str__(self) -> str:
        return self.username    
    
    def get_absolute_url(self):
        pass

    # not required but checker insists
    def check_password(self, raw_password: str) -> bool:
        if not self.password:
            raise ValidationError('You must provide a password')
        password = raw_password
        return super().check_password(password)

class MessageRepliesManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().select_related("replies")
    
class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user) -> models.QuerySet:
        return super().get_queryset().filter(receiver=user, read=False)

class Message(models.Model):

    message_id = models.UUIDField(
        verbose_name= 'Message ID',
        default= uuid.uuid4,
        primary_key= True,
        editable= False
    )

    sender = models.ForeignKey(
        to = User,
        on_delete= models.DO_NOTHING,
        related_name= 'sent_messages'
    )

    content = models.TextField(
        verbose_name='Message Content',
        null=False
    )

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    receiver = models.ForeignKey(
        to=User,
        on_delete=models.DO_NOTHING,
        related_name='recieved_messages'
    )

    edited = models.BooleanField(
        default= False
    )

    edited_at = models.DateTimeField(
        blank=True,
        null=True
    )

    edited_by = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    read = models.BooleanField(
        default= False)

    parent_message = models.ForeignKey(
        'self',
        on_delete= models.CASCADE,
        null= True,
        blank=True,
        related_name='replies'
    )

    objects = models.Manager()
    reply_objects = MessageRepliesManager()
    unread = UnreadMessagesManager()

    def __str__(self) -> str:
        return (
            f"{self.sender.username} : {self.content}"
            )
    
    class Meta:
        ordering = ['timestamp']

class MessageHistory(models.Model):

    message = models.OneToOneField(
        to=Message,
        on_delete=models.DO_NOTHING,
        related_name='old_messages'
    )

    old_content = models.TextField()



class Notification(models.Model):

    notification_id = models.UUIDField(
        primary_key= True,
        default= uuid.uuid4,
        editable=False)
    
    user = models.ForeignKey(
        to=User,
        on_delete= models.CASCADE,
        related_name='notifications')

    message = models.OneToOneField(
        to=Message,
        on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return f"{self.message.content[:10]} from {self.message.sender.email}"

class Conversation(models.Model):

    conversation_id = models.UUIDField(
        verbose_name= 'ID of Conversation',
        default= uuid.uuid4,
        primary_key= True,
        editable= False
    )

    participants = models.ManyToManyField(
        to=User,
        related_name='conversations'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def get_participants_names(self):
        participants_list = self.participants.all()
        return [x.username for x in participants_list]

    def __str__(self) -> str:
        return f"{self.conversation_id}, {self.created_at}. participants: {self.get_participants_names}"
    
    def get_absolute_url(self):
        return reverse('conversations-detail', kwargs={'pk':self.conversation_id})

