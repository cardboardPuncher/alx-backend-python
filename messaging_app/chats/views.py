from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['participants__username']

    def get_queryset(self):
        return self.queryset.filter(participants=self.request.user)

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['sent_at']

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')
        if conversation_id:
            return self.queryset.filter(conversation__conversation_id=conversation_id)
        return self.queryset.filter(conversation__participants=self.request.user)

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_id')
        if not conversation_id:
            return Response(
                {"detail": "Conversation ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(sender=self.request.user)
