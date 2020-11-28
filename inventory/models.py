from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
    description = models.CharField(max_length=100)
    mfr = models.CharField(max_length=100)
    cost = models.FloatField()
    inventory_qty = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.description} created by {self.owner} on {self.created_at}'

    def calculate_ext_cost(self):
        return self.inventory_qty*self.cost


class Order(models.Model):
    order_qty = models.IntegerField(default=1)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Ordered qty: {self.order_qty} of {self.item.description} on {self.created_at}'


class Usage(models.Model):
    usage_qty = models.IntegerField(default=1)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Used qty: {self.usage_qty} of {self.item.description} on {self.created_at}'
