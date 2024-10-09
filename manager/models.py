from django.db import models

# Create your models here.

class Configs(models.Model):
    pcentage = models.DecimalField(max_digits=10, decimal_places=2, default=0.01)

    def __str__(self):
        return self.pcentage