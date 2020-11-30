from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'), 

    # item urls
    path('item/', views.item_list, name='item-list'),
    path('item/create/', views.ItemCreate.as_view(), name='item-create'),
    path('item/<int:pk>/', views.item_detail, name='item-detail'),
    path('item/<int:pk>/update/', views.ItemDelete.as_view(), name='item-delete'),
    path('item/<int:pk>/delete/', views.ItemUpdate.as_view(), name='item-update'),

    # order urls
    path('item/<int:pk>/orders/', views.item_orders, name='item-orders'),
    path('item/<int:pk>/orders/form/', views.place_order, name='item-order-form'),

    # usage urls
    path('item/<int:pk>/usage/', views.item_usage, name='item-usage'),
    path('item/<int:pk>/usage/form/', views.use_item, name='item-usage-form'),
]
