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

@login_required
def dashboard(request):
    user_items = Item.objects.filter(owner=request.user)
    user_claims = Claim.objects.filter(item__owner=request.user, status='pending')
    return render(request, 'accounts/dashboard.html', {'user_items': user_items, 'user_claims': user_claims})

def claim_history_view(request):
    history_claims = Claim.objects.filter(item__owner=request.user).exclude(status='pending')
    return render(request, 'accounts/claim_history.html', {'history_claims': history_claims})
