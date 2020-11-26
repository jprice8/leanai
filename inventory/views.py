from django.shortcuts import render
from django.http import HttpResponse

from .models import Item


def index(request):
    context = {
        'item': Item.objects.all()
    }
    return render(request, 'inventory/landing.html', context)
