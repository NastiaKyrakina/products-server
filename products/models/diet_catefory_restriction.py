from django.db import models

from products.models import Category
from products.models.diet import Diet


class DietCategoryRestriction(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE)

    def __str__(self):
        return self.diet.name + ' ' + self.category.name