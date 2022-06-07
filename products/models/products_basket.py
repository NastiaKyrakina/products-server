from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class ProductsBasket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    creation_date = models.DateTimeField(auto_now_add=True)
    period = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(366)])
    max_sum = models.FloatField()
    products = models.JSONField()

    def __str__(self):
        return self.name
