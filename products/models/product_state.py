from django.db import models

PRODUCT_STATE_CHOICES = [
    ('AI', 'As is'),
    ('BL', 'Boiled'),
    ('BK', 'Baked'),
]


class ProductState(models.Model):
    dish_name = models.CharField(max_length=350)
    state = models.CharField(max_length=2, choices=PRODUCT_STATE_CHOICES)
    energy = models.DecimalField(max_digits=6, decimal_places=2)
    carbohydrates = models.DecimalField(max_digits=6, decimal_places=2)
    proteins = models.DecimalField(max_digits=6, decimal_places=2)
    fats = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.state + ' ' + self.dish_name
