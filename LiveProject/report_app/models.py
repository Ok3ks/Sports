from django.db import models


class GameweekScores(models.Model):
    __tablename__ = "Player_gameweek_score"

    index = models.IntegerField()
    player_id = models.IntegerField()  # there should be a foreign key here
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
    influence = models.IntegerField()
    creativity = models.IntegerField()
    threat = models.IntegerField()
    ict_index = models.IntegerField()
    starts = models.IntegerField()
    expected_goals = models.CharField()
    expected_assists = models.CharField()
    expected_goal_involvements = models.CharField()
    expected_goals_conceded = models.CharField()
    total_points = models.CharField()
    in_dreamteam = models.IntegerField()
    gameweek = models.IntegerField()

    class Meta:
        managed = False
        db_table = "Player_gameweek_score"
