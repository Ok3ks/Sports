from django.test import TestCase

# Create your tests here.

from models import Player

players = Player.objects.filter(position='Midfielder')
print(players)