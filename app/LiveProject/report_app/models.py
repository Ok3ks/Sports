from django.db import models

# Create your models here.

class Position(models.TextChoices):

    """Assigned Positions."""
    GK = "GoalKeeper", "GOALKEEPER",
    DEF = "Defender", "DEFENDER",
    MID = "Midfielder", "MIDFIELDER"
    FWD = "Forward", "FORWARD"


class Players(models.Model):
    
    index = models.IntegerField(primary_key=True)
    player_id = models.TextField()
    player_name = models.TextField()
    position = models.CharField(choices=Position.choices)
    team = models.TextField()
    half = models.IntegerField()

    class Meta:
        abstract = True
        managed = False
        db_table = "EPL_2024_PLAYER_INFO"

class Gameweek_Scores(models.Model):
    
    index = models.IntegerField(primary_key=True)
    player_id = models.IntegerField()
    minutes = models.IntegerField()
    goals_scored = models.IntegerField()
    assists = models.IntegerField()
    clean_sheets = models.IntegerField()
    goals_conceded = models.IntegerField()
    own_goals = models.IntegerField()
    penalties_saved = models.IntegerField()
    penalties_missed = models.IntegerField()
    yellow_cards = models.IntegerField()
    red_cards = models.IntegerField()
    saves = models.IntegerField()
    bonus = models.IntegerField()
    bps = models.IntegerField()
    influence = models.FloatField()
    creativity = models.FloatField()
    threat = models.FloatField()
    ict_index = models.FloatField()
    starts = models.IntegerField()
    expected_goals = models.FloatField()
    expected_assists = models.FloatField()
    expected_goal_involvements = models.FloatField()
    expected_goals_conceded = models.FloatField()
    total_points = models.IntegerField()
    in_dreamteam = models.IntegerField()
    gameweek = models.IntegerField()

    class Meta:
        abstract = True
        managed = False
        db_table = "Player_gameweek_score"