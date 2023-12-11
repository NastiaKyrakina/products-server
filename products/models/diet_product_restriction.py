from django.db import models

from products.models import Restriction
from products.models.diet import Diet


class DietProductRestriction(models.Model):
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE)
    restriction = models.ForeignKey(Restriction, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.diet.name + ' ' + self.restriction.product.name + ' ' + self.restriction.comparator + ' ' + str(self.restriction.amount)