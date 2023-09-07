from django.db import models

class SecuritySettings(models.Model):
    name = models.CharField(max_length=250)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name + ': ' + ('Enabled' if self.enabled else 'Disabled')

class SecurityQuestions(models.Model):
    question = models.CharField(max_length=250)
    answer = models.CharField(max_length=250)

    def __str__(self):
        return self.question