from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView, CreateView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, viewsets

from .models import Item, Order, Usage
from .forms import PlaceOrderForm, UsageForm
from .serializers import ItemSerializer, OrderSerializer, UsageSerializer


def index(request):
    context = {
        'item_list': Item.objects.all()
    }
    return render(request, 'inventory/landing.html', context)


# Item views
@login_required
def item_list(request):
    context = {
        'item_list': Item.objects.filter(owner=request.user)
    }
    return render(request, 'inventory/overview.html', context)


@login_required
def item_detail(request, pk):
    item_from_id = get_object_or_404(Item, pk=pk)
    context = {
        'item': item_from_id,
    }
    return render(request, 'inventory/item_detail.html', context)


class ItemCreate(LoginRequiredMixin, CreateView):
    model = Item
    fields = ['description', 'mfr', 'inventory_qty', 'cost']
    template_name = 'inventory/item_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ItemUpdate(LoginRequiredMixin, UpdateView):
    model = Item
    fields = ['description', 'mfr', 'inventory_qty', 'cost']
    template_name = 'inventory/item_form.html'


class ItemDelete(LoginRequiredMixin, DeleteView):
    model = Item
    success_url = '/item/'
    template_name = 'inventory/item_confirm_delete.html'


# Order views
@login_required
def item_orders(request, pk):
    item_from_id = get_object_or_404(Item, pk=pk)
    orders = Order.objects.filter(item=item_from_id)
    context = {
        'item': item_from_id,
        'orders': orders,
    }
    return render(request, 'inventory/item_orders.html', context)


@login_required
def place_order(request, pk):
    item_from_id = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = PlaceOrderForm(request.POST)
        if form.is_valid():
            # Use quantity entered to update our inventory
            qty = form.cleaned_data['order_qty']

            if qty > 0:
                # Update item's inventory
                item_from_id.inventory_qty += qty
                item_from_id.save()

                # Add new order to order db
                new_order = Order(order_qty=qty, item=item_from_id)
                new_order.save()

            # redirecct to a new url
            return HttpResponseRedirect(reverse('item-orders', args=(pk,)))
        # if GET request, create a blank form
    else:
        form = PlaceOrderForm()

    return render(request, 'inventory/item_order_form.html', {
        'form': form,
        'item': item_from_id,
    })


# Usage views
@login_required
def item_usage(request, pk):
    item_from_id = get_object_or_404(Item, pk=pk)
    usage = Usage.objects.filter(item=item_from_id)
    context = {
        'item': item_from_id,
        'usage': usage,
    }
    return render(request, 'inventory/item_usage.html', context)


@login_required
def use_item(request, pk):
    item_from_id = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = UsageForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data['usage_qty']

            if 0 < qty <= item_from_id.inventory_qty:
                item_from_id.inventory_qty -= qty
                item_from_id.save()

            new_usage = Usage(usage_qty=qty, item=item_from_id)
            new_usage.save()

        return HttpResponseRedirect(reverse('item-usage', args=(pk,)))

    else:
        form = UsageForm()
    return render(request, 'inventory/item_usage_form.html', {
        'form': form,
        'item': item_from_id
    })


# Api views
@login_required
def get_data(request, pk):
    data = {
        "sales": 100,
        "customers": 10,
    }

    return JsonResponse(data)


@login_required
def get_order_data(request, pk):
    static_labels = ["January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"]
    static_orders = [4, 3, 5, 1, 3, 4, 4, 4, 2, 3, 4, 3]
    
    item_from_id = get_object_or_404(Item, pk=pk)
    dynamic_orders = Order.objects.filter(item=item_from_id)
    

    view_data = {
        # "static_labels": static_labels,
        # "static_orders": static_orders,
        # "dynamic_orders": dynamic_orders.values('order_qty'),
        # "item_from_id": item_from_id,
        "labels": static_labels,
        "default": static_orders,
    }

    return JsonResponse(view_data)


# Django rest framework views
class GetTestData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        order_count = Order.objects.all().count()
        labels = ["Orders", "Blue", "Yellow", "Green", "Purple", "Orange"]
        default_items = [order_count, 12, 32, 12, 18]

        drf_data = {
            "labels": labels,
            "default": default_items,
            "orders": order_count,
        }
        return Response(drf_data)


class GetOrdersForItem(APIView):
    """
    Retrieve, update, or delete an order instance.
    """

    def get_object(self, pk):
        try:
            item_from_id = get_object_or_404(Item, pk=pk)
            orders = Order.objects.filter(item=item_from_id)
            return orders
        except Order.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        labels = ["Yellow", "Green", "Purple", "Orange"]
        default_items = [12, 32, 12, 18]

        orders = self.get_object(pk)
        serializer = OrderSerializer(orders, many=True)

        drf_data = {
            "labels": labels,
            "default": default_items,
            "orders": serializer.data,
        }

        return Response(drf_data)



class GetUsageForItem(APIView):
    """
    Retrieve, update, or delete usage instance.
    """

    def get_object(self, pk):
        try:
            item_from_id = get_object_or_404(Item, pk=pk)
            usage = Usage.objects.filter(item=item_from_id)
            return usage
        except Usage.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        usage = self.get_object(pk)
        serializer = UsageSerializer(usage, many=True)

        drf_data = {
            "usage": serializer.data,
        }

        return Response(drf_data)
