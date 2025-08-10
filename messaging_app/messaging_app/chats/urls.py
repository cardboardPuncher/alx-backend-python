from rest_framework import routers
from django.urls import path, include
from chats.views import (
    MessageViewSet, ConversationViewSet, get_token,
    UserViewSet, log_out)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)



NestedDefaultRouter = routers.DefaultRouter()
NestedDefaultRouter.register(r'messages', MessageViewSet, basename='messages')
NestedDefaultRouter.register(r'conversations', ConversationViewSet, basename='conversations')
NestedDefaultRouter.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(NestedDefaultRouter.urls)),
    path('get_token/', get_token, name='get-token'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', log_out, name='log_out')
]