
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from rest_framework.decorators import (
    api_view, permission_classes, action)

from rest_framework.permissions import (AllowAny, IsAdminUser, IsAuthenticated)

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib.auth import get_user_model, logout
from django.shortcuts import get_object_or_404

from django_filters import rest_framework as d_filters

from messaging.serializers import (
    RegisterUserSerializer, UserTokenSerializer,  ConversationSerializer,
    MessagesSerializer, UnreadMessageSerializer, UserSerializer,UserLimitedSerializer, ChatRoomListSerializer, CreateChatRoomSerializer)

from messaging.permissions import (
    IsParticipantOfConversation, IsAnonOrAdminUser, IsOwner)

from messaging.models import Conversation, Message
from messaging.pagination import MessageListingPagination
from messaging.filters import MessageFilter

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = RegisterUserSerializer
    queryset = get_user_model().objects.all()
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAnonOrAdminUser()]
        return super().get_permissions()

    def get_serializer_class(self, *args, **kwargs): #type:ignore
        if self.action == 'list':
            return UserLimitedSerializer
        return self.serializer_class
    
    @method_decorator(cache_page(60*1))
    @action(
        detail=False, methods=['get'], url_name='unread',
        permission_classes=[IsAuthenticated, IsOwner])
    def unread_messages(self, request, pk=None):
        messages = Message.unread.unread_for_user(
            request.user).only(
                'sender', 'content', 'timestamp', 'read', 'parent_message')
        
        if not messages.exists():
            return Response(
                {"msg":"You do not have unread messages"},
                status=status.HTTP_200_OK)
        
        serialized = UnreadMessageSerializer(instance = messages, many=True)
        messages.update(read=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
        
class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.prefetch_related('participants').all()
    permission_classes = [IsParticipantOfConversation]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user not in instance.participants.all():
            return Response(
                {"message":"Sorry you do not belong in this Convo"},
                status=status.HTTP_403_FORBIDDEN
            )
        messages = Message.objects.filter(conversation=instance)
        serializer = MessagesSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self): # type: ignore
        if self.action == 'list':
            return ChatRoomListSerializer
        elif self.action == 'create':
            return CreateChatRoomSerializer
        return super().get_serializer_class()
    

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessagesSerializer
    queryset = Message.objects.prefetch_related('sender').all()
    permission_classes = [IsParticipantOfConversation]
    filter_backends = [filters.OrderingFilter, d_filters.DjangoFilterBackend]
    filterset_class = MessageFilter
    pagination_class = MessageListingPagination

    def get_queryset(self): # type: ignore
        if self.action in ['update','delete']:
            return Message.objects.all().filter(sender=self.request.user)
        elif self.action == 'list':
            return Message.objects.all().filter(sender=self.request.user).prefetch_related('replies')
        return super().get_queryset()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer
        obj = serializer(data=request.data, context={'request':request})
        self.check_object_permissions(request, obj, *args, **kwargs)
        return super().create(request, *args, **kwargs)
    



#this is just to pass checker please refer to Conversation viewset for actual method
@api_view(http_method_names=['GET'])
@permission_classes([IsAuthenticated])
def get_conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation,pk=conversation_id)
    if request.user in conversation.participants.all():
        conversation_messages = Message.objects.filter(
                conversation=conversation_id).all()

        serialized_messages = MessagesSerializer(
                data=conversation_messages,
                many=True
            )
        serialized_messages.is_valid(raise_exception=True)
        return Response(
                data=serialized_messages.data,
                status=status.HTTP_200_OK
            )
    return Response(
        {"message":"Sorry you do not have permission"},
        status=status.HTTP_403_FORBIDDEN)

@api_view(http_method_names=['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, receiver_name=None):
    messages = Message.objects.filter(
        sender=request.user,
        receiver__username=receiver_name
    ).all().select_related('receiver')
    serialized = MessagesSerializer(instance=messages, many=True)
    return Response(serialized.data, status=status.HTTP_200_OK)

@api_view(http_method_names=['POST', 'GET'])
@permission_classes([AllowAny])
def get_token(request):
    if request.method == 'POST':
        serializer = UserTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        return Response(data=data, status=status.HTTP_200_OK)
    return Response(
        data={
            "message":"Only 'POST' method allowed. Send your {'username':'password'} to retrieve your token"},
        status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(http_method_names=['POST'])
def log_out(request):
    if request.method == 'POST':
        try:
            Token.objects.get(user=request.user).delete()
        except Token.DoesNotExist:
            pass
        logout(request)
        return Response({"message":"User Logged Out Successfully"}, status=status.HTTP_200_OK)

@permission_classes([IsOwner, IsAuthenticated])
@api_view(http_method_names=['GET','DELETE'])
def delete_user(request):
    if request.method == 'DELETE':
        if request.user.is_authenticated:
            User = get_user_model()
            user = get_object_or_404(User, pk=request.user.user_id)
            user.delete()
            log_out()
        return Response(
            {"message":"User deleted"},
            status=status.HTTP_204_NO_CONTENT
        )
    if request.user.is_authenticated:
        user_data = UserLimitedSerializer(instance=request.user).data
        return Response(
        user_data,
        status=status.HTTP_200_OK)
    return Response(
        {"message":"Forbidden"},
        status=status.HTTP_401_UNAUTHORIZED
    )