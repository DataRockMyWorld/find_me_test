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
from django.views.generic import UpdateView, DeleteView


class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    context_object_name = 'conversations'
    template_name = 'messaging/conversation_list.html'

    def get_queryset(self):
        return self.request.user.conversations.all().distinct()

class ConversationDetailView(LoginRequiredMixin, DetailView):
    model = Conversation
    context_object_name = 'conversation'
    template_name = 'messaging/conversation_detail.html'

    def get_queryset(self):
        # Ensure the user is a participant of the conversation
        return self.request.user.conversations.all()
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.messages.exclude(sender=self.request.user).update(is_read=True)  # Mark as read
        return response
    

class SendMessageView(CreateView):
    model = Message
    fields = ['content']
    template_name = 'messaging/send_message.html'

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.conversation_id = self.kwargs.get('conv_id')
        return super().form_valid(form)
    

    def get_success_url(self):
        # Redirect to the conversation detail page or another success page
        return reverse_lazy('conversation_detail', kwargs={'pk': self.object.conversation_id})


@login_required
def message_user(request, user_id):
    other_user = get_object_or_404(get_user_model(), id=user_id)
    if request.user == other_user:
        messages.error(request, "You cannot create a conversation with yourself.")
        return redirect('dashboard')
    
    # Try to get an existing conversation or create a new one if it doesn't exist
    conversation, created = Conversation.objects.get_or_create_between(request.user, other_user)
    return redirect('conversation_detail', pk=conversation.pk)

class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ['content']
    template_name = 'messaging/edit_message.html'
    success_url = reverse_lazy('conversation_list')  # Redirect as appropriate

    def get_queryset(self):
        return super().get_queryset().filter(sender=self.request.user)

class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'messaging/confirm_delete.html'
    success_url = reverse_lazy('conversation_list')  # Redirect as appropriate

    def get_queryset(self):
        return super().get_queryset().filter(sender=self.request.user)