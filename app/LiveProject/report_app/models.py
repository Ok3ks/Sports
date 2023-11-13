from django.db import models

# Create your models here.
class Player(models.Model):
    #Use DB for this - fairly constant, but start with json
    player_id = models.IntegerField(max_length=5)
    position = models.CharField(max_length = 10)
    team = models.CharField(max_length= 100)
    player = models.CharField(max_length=100)
