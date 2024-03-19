from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from .models import Item, Category, Notification
from claims.models import Claim
from .forms import ItemForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from claims.forms import ClaimForm



class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    context_object_name = 'items'
    template_name = 'items/item_list.html'

    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user)

class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'items/item_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('item-list')

class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'items/item_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        item = self.get_object()
        return self.request.user == item.owner
    
    def get_success_url(self):
        return reverse_lazy('item-list')

class ItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Item
    context_object_name = 'item'
    template_name = 'items/item_confirm_delete.html'
    success_url = reverse_lazy('item-list')

    def test_func(self):
        item = self.get_object()
        return self.request.user == item.owner
    
from django.views.generic import ListView
from .models import Category

class CategoryListView(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'items/category_list.html'


def home(request):
    query = request.GET.get('q')
    items = None
    if query:
        items = Item.objects.filter(title__icontains=query)
    return render(request, 'items/home.html', {'items': items})

def lost_items(request):
    items = Item.objects.filter(status='lost')
    return render(request, 'items/items_list.html', {'items': items, 'title': 'Lost Items'})

def found_items(request):
    items = Item.objects.filter(status='found')
    return render(request, 'items/items_list.html', {'items': items, 'title': 'Found Items'})

def item_detail(request, id):
    item = get_object_or_404(Item, id=id)
    return render(request, 'items/item_detail.html', {'item': item})

def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('items/item_detail', id=item.id)
    else:
        form = ItemForm(instance=item)
    return render(request, 'items/edit_item.html', {'form': form, 'item': item})

@login_required
def make_claim(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if item.owner == request.user:
        messages.error(request, "You cannot claim your own item.")
        return redirect('dashboard')

    Claim.objects.get_or_create(item=item, claimant=request.user)
    send_mail(
        'New Claim on Your Item',
        'There has been a new claim made on your item. Please check your dashboard to approve or reject it.',
        'from@example.com',
        [item.owner.email],
        fail_silently=False,
    )
    messages.success(request, "Claim made successfully. The owner has been notified.")
    return redirect('dashboard')

@login_required
def approve_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    if claim.item.owner != request.user:
        messages.error(request, "You are not authorized to approve this claim.")
        return redirect('dashboard')  # Replace 'dashboard' with your dashboard view's name

    claim.status = 'approved'
    claim.save()

    # Send notification
    Notification.objects.create(
        recipient=claim.claimant,
        item=claim.item,
        type='claim_approved',
        message=f'Your claim on {claim.item.title} has been approved.'
    )
    
    # Optionally, send an email notification
    send_mail(
        'Claim Approved',
        f'Your claim on {claim.item.title} has been approved by the owner.',
        'from@example.com',
        [claim.claimant.email],
        fail_silently=False,
    )

    messages.success(request, "Claim approved successfully.")
    return redirect('dashboard')

@login_required
def reject_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    if claim.item.owner != request.user:
        messages.error(request, "You are not authorized to reject this claim.")
        return redirect('dashboard')

    claim.status = 'rejected'
    claim.save()

    # Send notification
    Notification.objects.create(
        recipient=claim.claimant,
        item=claim.item,
        type='claim_rejected',
        message=f'Your claim on {claim.item.title} has been rejected.'
    )
    
    # Optionally, send an email notification
    send_mail(
        'Claim Rejected',
        f'Your claim on {claim.item.title} has been rejected by the owner.',
        'from@example.com',
        [claim.claimant.email],
        fail_silently=False,
    )

    messages.success(request, "Claim rejected successfully.")
    return redirect('dashboard')

class ClaimCreateView(LoginRequiredMixin, View):
    def get(self, request, item_id):
        item = get_object_or_404(Item, pk=item_id)
        form = ClaimForm()
        return render(request, 'items/claim_form.html', {'form': form, 'item': item})

    def post(self, request, item_id):
        item = get_object_or_404(Item, pk=item_id)
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.item = item
            claim.claimer = request.user  # Assuming you have a claimer field to store who made the claim
            claim.save()
            # Redirect to a confirmation page, item detail, or dashboard
            return redirect('dashboard')
        return render(request, 'items/claim_form.html', {'form': form, 'item': item})
    

def claim_detail_view(request, claim_id):
    claim = get_object_or_404(Claim, pk=claim_id)
    return render(request, 'items/claim_detail.html', {'claim': claim})