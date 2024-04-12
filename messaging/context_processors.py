from .models import Conversation, Message

def message_count(request):
    if request.user.is_authenticated:
        # Count the number of unread messages
        unread_count = Message.objects.filter(conversation__participants=request.user, is_read=False).exclude(sender=request.user).count()
        return {'messages_count': unread_count}
    return {'messages_count': 0}
