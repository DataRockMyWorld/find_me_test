from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from .models import Item, Claim
from .forms import ClaimForm
from django.contrib.auth.mixins import LoginRequiredMixin

class ClaimCreateView(LoginRequiredMixin, View):
    def get(self, request, item_id):
        item = get_object_or_404(Item, pk=item_id)
        form = ClaimForm()
        return render(request, 'claim_form.html', {'form': form, 'item': item})

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
        return render(request, 'claim_form.html', {'form': form, 'item': item})
