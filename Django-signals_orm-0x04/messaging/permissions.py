from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    def has_permission(self, request, view): # type: ignore
        if request.user.is_authenticated:
            return True
        return False
    
    def has_object_permission(self, request, view, obj): # type: ignore
        from messaging.views import ConversationViewSet, MessageViewSet
        #check if the user is the same as the message sender
        if isinstance(view, MessageViewSet):
            if view.action == 'create':
                return True
            if obj.sender == request.user:
                return True
        if isinstance(view, ConversationViewSet):
            if request.user in obj.participants.all():
                if request.method in ['GET','PUT', 'PATCH', 'DELETE']:
                    return True
        return False
        

class IsAnonOrAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):  # type: ignore
        if request.user.is_anonymous or request.user.is_superuser:
            return True
        return False
    
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user
