from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Game(models.Model):
    appid = models.IntegerField()
    name = models.CharField(max_length=250)
    thumb_nail = models.URLField()
    price = models.IntegerField()

    def __str__(self):
        return self.name

class Watchlist(models.Model):
    name = models.CharField(max_length=100)
    games = models.ManyToManyField(Game, through='PriceCheck')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("watchlist-detail", kwargs={"pk": self.id})
    
class PriceCheck(models.Model):
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    target_price = models.IntegerField(default=0)