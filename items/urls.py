from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('index/', views.index, name="index"),
    path('item/', views.ItemListView.as_view(), name='item-list'),
    path('new/', views.ItemCreateView.as_view(), name='item-create'),
    path('<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item-update'),
    path('<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item-delete'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('', views.home, name='home'),
    path('lost/', views.lost_items, name='lost_items'),
    path('found/', views.found_items, name='found_items'),
    path('item/<int:id>/', views.item_detail, name='item_detail'),
    path('item/edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('items/<int:item_id>/claim/', views.make_claim, name='make_claim'),
    path('claims/<int:claim_id>/approve/', views.approve_claim, name='approve_claim'),
    path('claims/<int:claim_id>/reject/', views.reject_claim, name='reject_claim'),
    path('item/<int:item_id>/claim/', views.ClaimCreateView.as_view(), name='claim_create'),
    path('claim/<int:claim_id>/', views.claim_detail_view, name='claim_detail'),
]
