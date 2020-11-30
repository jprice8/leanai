from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView, CreateView

from .models import Item, Order, Usage
from .forms import PlaceOrderForm, UsageForm


def index(request):
    context = {
        'item_list': Item.objects.all()
    }
    return render(request, 'inventory/landing.html', context)

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
