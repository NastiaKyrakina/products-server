from django.db import models


class Diet(models.Model):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=1000)
    carbMin = models.DecimalField(max_digits=6, decimal_places=2)
    carbMax = models.DecimalField(max_digits=6, decimal_places=2)
    protMin = models.DecimalField(max_digits=6, decimal_places=2)
    protMax = models.DecimalField(max_digits=6, decimal_places=2)
    fatsMin = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fatsMax = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name
