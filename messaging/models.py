from django.db import models
from django.db.models import Count
from django.conf import settings

class ConversationManager(models.Manager):
    def get_or_create_between(self, user1, user2):
        if user1 == user2:
            raise ValueError("Cannot create a conversation with the same user.")

        # Check for an existing conversation between user1 and user2
        conversation = self.get_queryset().annotate(
            num_participants=Count('participants')
        ).filter(
            participants=user1
        ).filter(
            participants=user2
        ).filter(
            num_participants=2
        ).first()

        # If no such conversation exists, create one
        if conversation is None:
            conversation = self.model()
            conversation.save()
            conversation.participants.add(user1, user2)
            created = True
        else:
            created = False
            

        return conversation, created


class Conversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="conversations")

    objects = ConversationManager()

    def __str__(self):
        return f"Conversation between {', '.join(self.participants.values_list('username', flat=True))}"



class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username} on {self.timestamp}"

