from django.db import models
from .product import Product
from .product_state import ProductState


class ShopProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=350)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    unit = models.CharField(max_length=3)
    states = models.ManyToManyField(ProductState)
    default = models.BooleanField(default=True)

    def __str__(self):
        return self.name