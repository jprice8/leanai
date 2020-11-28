from django.shortcuts import render
from django.http import HttpResponse

from .models import Item


def index(request):
    context = {
        'item_list': Item.objects.all()
    }
    return render(request, 'inventory/landing.html', context)


def item_list(request):
    context = {
        'item_list': Item.objects.all()
    }
    return render(request, 'inventory/overview.html', context)

