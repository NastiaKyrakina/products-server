from django.db import models
from .category import Category


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=350)

    def __str__(self):
        return self.name