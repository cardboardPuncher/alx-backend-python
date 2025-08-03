from rest_framework import serializers
from .models import Conversation, Message, MessageHistory
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'first_name',
            'last_name',
            'email',
            # 'password',
            'role',
            'phone_number'
            ]
        # extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = [
            'role'
        ]

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = [
            'user_id'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserTokenSerializer(serializers.Serializer):
    """
    Serializer class to authenticate users and return Token
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()

    def get_token(self,obj):
        try:    
            user = authenticate(
                username= obj.get('username'),
                password=obj.get('password')
            )
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                return token.key
        except AuthenticationFailed:
            raise

    def validate(self, attrs):
        s = authenticate(
            username=attrs['username'],
            password=attrs['password']
            )
        if s is None:
            raise AuthenticationFailed("{'error':'Wrong username or password'}")
        return super().validate(attrs)
        


class MessageHistorySerializer(serializers.ModelSerializer):
    edited_at = serializers.SerializerMethodField()
    edited_by = serializers.SerializerMethodField()
    class Meta:
        model = MessageHistory
        fields = ['old_content', 'edited_at','edited_by']

    def get_edited_at(self, obj):
        return obj.message.edited_at
    
    def get_edited_by(self, obj):
        message_sender = obj.message.sender.email
        return message_sender

class UnreadMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = [
            'parent_message',
            'sender',
            'content',
            'timestamp',
        ]

    def get_sender(self, obj):
        return obj.sender.email

class MessageReplySerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    # receiver = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = [
            # 'parent_message',
            'sender',
            'content',
            # 'receiver'
        ]

    def get_sender(self, obj):
        return obj.sender.email
    
    def get_receiver(self, obj):
        return obj.receiver.email


class MessagesSerializer(serializers.ModelSerializer):
    # sender = serializers.SerializerMethodField()
    old_message = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    receiver = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = [
            # 'sender',
            'receiver',
            'content',
            'timestamp',
            # 'conversation',
            'old_message',
            'replies'
        ]

    def validate(self, attrs):
        return super().validate(attrs)

    def get_receiver(self, obj):
        return obj.receiver.email
    
    def get_sender(self, obj):
        return obj.sender.email
    
    def get_old_message(self, obj):
        try:
            msg = obj.old_messages
            serialized = MessageHistorySerializer(instance=msg)
            return serialized.data
        except MessageHistory.DoesNotExist:
            return {"info":"Message Not Edited"}
    
    def get_replies(self, obj):
        msg_replies = obj.replies.all()
        serialized = MessageReplySerializer(instance=msg_replies, many=True)
        return serialized.data
    

# class MessageHistorySerializer(serializers.ModelSerializer):
    # class Meta:
        # model = MessageHistory
        # fields = ['old_content']

class UserLimitedSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'messages'
        ]
    def get_messages(self, obj):
        messages = obj.sent_messages.all()
        return MessagesSerializer(
            instance=messages,
            many=True,
            context=self.context).data

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserLimitedSerializer(many=True, read_only=True)
    messages = MessagesSerializer(many=True, read_only=True)
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'messages'
        ]

class CreateChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            'participants'
        ]
    
    def validate(self, attrs):
        user = self.context['request'].user
        participants = attrs.get('participants', [])
        if user not in participants:
            participants.append(user)
        attrs['participants'] = participants
        if len(attrs.get('participants')) < 2:
            raise serializers.ValidationError("Chat Room must have more than 1 User")
        return attrs

class ChatRoomListSerializer(serializers.ModelSerializer):
    participants = UserLimitedSerializer(many=True)
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants'
        ]
        read_only_fields = [
            'conversation_id',
            'participants'
        ]

