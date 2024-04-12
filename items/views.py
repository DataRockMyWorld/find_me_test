from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from .models import Item, Category, Notification
from claims.models import Claim
from .forms import ItemForm, ItemSearchForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from claims.forms import ClaimForm
from django.conf import settings
from django.views.decorators.http import require_http_methods



class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    context_object_name = 'items'
    template_name = 'items/items_list.html'

    def get_queryset(self):
        # Start with all items or limit to the user's items based on your needs
        items = Item.objects.all()  # or .filter(owner=self.request.user) for user's items

        # Instantiate the search form with GET data
        self.form = ItemSearchForm(self.request.GET)

        if self.form.is_valid():
            if query := self.form.cleaned_data.get('query'):
                items = items.filter(title__icontains=query)
            if category := self.form.cleaned_data.get('category'):
                items = items.filter(category=category)
            if status := self.form.cleaned_data.get('status'):
                items = items.filter(status=status)
            if location := self.form.cleaned_data.get('location'):
                items = items.filter(location__icontains=location)
            if sort_by := self.form.cleaned_data.get('sort_by'):
                if sort_by == 'newest':
                    items = items.order_by('-date_posted')
                elif sort_by == 'oldest':
                    items = items.order_by('date_posted')

        return items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the form to the context
        context['form'] = self.form
        return context

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
            print("Item saved successfully")
            return redirect('item_detail', id=item.id)
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
@require_http_methods(["POST"])  # Ensure that these views only accept POST requests.
def approve_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    if claim.item.owner != request.user:
        messages.error(request, "You are not authorized to approve this claim.")
        return redirect('dashboard')

    if claim.status == 'pending':  # Ensure only pending claims can be approved.
        claim.status = 'approved'
        claim.save()
        messages.success(request, "Claim approved successfully.")
    else:
        messages.info(request, "This claim has already been processed.")

    return redirect('dashboard')

@login_required
@require_http_methods(["POST"])
def reject_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    if claim.item.owner != request.user:
        messages.error(request, "You are not authorized to reject this claim.")
        return redirect('dashboard')

    if claim.status == 'pending':  # Ensure only pending claims can be rejected.
        claim.status = 'rejected'
        claim.save()
        messages.success(request, "Claim rejected successfully.")
    else:
        messages.info(request, "This claim has already been processed.")

    return redirect('dashboard')

class ClaimCreateView(LoginRequiredMixin, View):
    def get(self, request, item_id):
        item = get_object_or_404(Item, pk=item_id)
        form = ClaimForm()
        return render(request, 'items/claim_form.html', {'form': form, 'item': item})

    def post(self, request, item_id):
        item = get_object_or_404(Item, pk=item_id)
        existing_claim = Claim.objects.filter(item=item, claimant=request.user).exists()
        if existing_claim:
            messages.error(request, "You have already made a claim on this item.")
            return redirect('item_detail', id=item_id)
            
        
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.item = item
            claim.claimant = request.user  # Assuming you have a claimer field to store who made the claim
            claim.save()
            messages.success(request, "Your claim has been submitted successfully.")
            # Redirect to a confirmation page, item detail, or dashboard
            return redirect('dashboard')
        return render(request, 'items/claim_form.html', {'form': form, 'item': item})
    

def claim_detail_view(request, claim_id):
    claim = get_object_or_404(Claim, pk=claim_id)
    return render(request, 'items/claim_detail.html', {'claim': claim})


def index(request):
    return render(request, 'items/index.html')