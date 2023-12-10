from django.db import models

from products.models import Product
from products.models.diet import Diet


class DietProductRestriction(models.Model):
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    min = models.DecimalField(max_digits=6, decimal_places=2)
    max = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.diet.name + ' ' + self.product.name