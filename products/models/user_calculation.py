from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from products.models import ShopProduct, Restriction

SEX_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
]

ACTIVITY_CHOICES = [
    ('1', 'lowest'),
    ('2', 'low'),
    ('3', 'medium'),
    ('4', 'high'),
    ('5', 'highest'),
]


class UserCalculations(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    height = models.FloatField()
    weight = models.FloatField()
    years = models.IntegerField()
    sex = models.CharField(max_length=2, choices=SEX_CHOICES)
    activity_level = models.CharField(max_length=2, choices=ACTIVITY_CHOICES)

    def __str__(self):
        return self.user.username


class UserProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop_product = models.ForeignKey(ShopProduct, on_delete=models.CASCADE)


class UserRestriction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restriction = models.ForeignKey(Restriction, on_delete=models.CASCADE)
