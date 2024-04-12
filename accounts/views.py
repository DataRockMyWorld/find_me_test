from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import SignUpForm
from items.models import Item
from django.contrib.auth.decorators import login_required
from claims.models import Claim
from django.contrib import messages
from .models import UserProfile

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your account has been created successfully!')
            return redirect('home')  # Redirect to your app's home page
        else:
            messages.error(request, 'Please correct the error below.')        
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})
"""
@login_required
def dashboard(request):
    user_items = Item.objects.filter(owner=request.user)
    user_claims = Claim.objects.filter(item__owner=request.user, status='pending')
    return render(request, 'accounts/dashboard.html', {'user_items': user_items, 'user_claims': user_claims})
"""
@login_required
def dashboard(request):
    user = request.user

    # Incoming Claims are claims on user's items
    incoming_claims = Claim.objects.filter(item__owner=user, status='pending').select_related('item', 'claimant')

    # Outgoing Claims are claims made by the user on others' items
    outgoing_claims = Claim.objects.filter(claimant=user).exclude(item__owner=user).select_related('item', 'item__owner')

    # Claim History for claims that have been processed
    claim_history = Claim.objects.filter(claimant=user, status__in=['approved', 'rejected']).select_related('item', 'item__owner')

    context = {
        'user_items': Item.objects.filter(owner=user),
        'incoming_claims': incoming_claims,
        'outgoing_claims': outgoing_claims,
        'claim_history': claim_history,
    }
    return render(request, 'accounts/dashboard.html', context)


def claim_history_view(request):
    history_claims = Claim.objects.filter(item__owner=request.user).exclude(status='pending')
    return render(request, 'accounts/claim_history.html', {'history_claims': history_claims})
