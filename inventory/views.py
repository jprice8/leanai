from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Item


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

