# messaging/views.py

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Conversation, Message
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages


class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    context_object_name = 'conversations'
    template_name = 'messaging/conversation_list.html'

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user).distinct()

class ConversationDetailView(LoginRequiredMixin, DetailView):
    model = Conversation
    context_object_name = 'conversation'
    template_name = 'messaging/conversation_detail.html'

    def get_queryset(self):
        # Ensure the user is a participant of the conversation
        return Conversation.objects.filter(participants=self.request.user)
    

class SendMessageView(CreateView):
    model = Message
    fields = ['content', 'conversation']  # Assuming you have a way for the user to choose the conversation
    template_name = 'messaging/send_message.html'

    def form_valid(self, form):
        # Assume the conversation is correctly set in the form.
        # Now, set the sender and determine the receiver based on the conversation's participants.
        conversation = form.cleaned_data.get('conversation')
        form.instance.sender = self.request.user

        # Logic to determine the receiver within the conversation
        # This is a simplistic approach for two-person conversations.
        other_participants = conversation.participants.exclude(id=self.request.user.id)
        if other_participants.exists():
            form.instance.receiver = other_participants.first()
        else:
            # Handle error or invalid conversation scenario
            pass

        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the conversation detail page or another success page
        return reverse_lazy('conversation_detail', kwargs={'pk': self.object.conversation_id})


@login_required
def message_user(request, user_id):
    recipient = get_object_or_404(get_user_model(), id=user_id)
    
    # Prevent users from messaging themselves
    if recipient == request.user:
        messages.error(request, "You cannot create a conversation with yourself.")
        return redirect('dashboard')  # Redirect to an appropriate view

    conversation = Conversation.objects.get_or_create_between(request.user, recipient)
    
    # Redirect to the conversation detail view or a message creation view
    return redirect('conversation_detail', pk=conversation.pk)