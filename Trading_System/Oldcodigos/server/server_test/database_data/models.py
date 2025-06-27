from django.db import models

class Stock(models.Model):
    especie = models.CharField(max_length=20)
    time = models.DateTimeField()
    open = models.FloatField()
    close = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    fuente = models.CharField(max_length=20)
    fechaDato = models.DateField()
    tipoDato = models.CharField(max_length=20)
