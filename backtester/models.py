from django.db import models

class ForexData(models.Model):
    currency_pair = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    open_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    close_price = models.FloatField()
    volume = models.FloatField()

    def __str__(self):
        return f"{self.currency_pair} - {self.timestamp}"
