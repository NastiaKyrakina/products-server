from django.db import models

from . import Product
from .category import Category

COMPARATORS = [
    ('EQ', 'equal'),
    ('GT', 'Great than'),
    ('LT', 'Less than'),
]


class Restriction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    comparator = models.CharField(max_length=2, choices=COMPARATORS)
    amount = models.FloatField()
    unit = models.CharField(max_length=3)
    default = models.BooleanField(default=True)

    def __str__(self):
        return self.product.name + ' ' + self.comparator + ' ' + str(self.amount)
