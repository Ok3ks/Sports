import json
import os 
import requests

FIXTURES = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
FIXTURES_STATS = fixtures_stats = "https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics"

ACCESS_KEY = os.get_env("X-RapidAPI-Key")

class API_BETS():
    def __init__(self,season, league_id):
        self.season = season
        self.league_id = league_id

    def api_init(self,league_id, season):
        fixture_params = {"league": self.league_id, "season": self.season}
        headers = {
            "X-RapidAPI-Key": ACCESS_KEY,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        return fixture_params, headers
    
    def query_web(header = headers, params = params, endpoint = "fixtures"):
        
        if endpoint == "fixtures":
            response = requests.get(FIXTURES, headers=header, params=params)
        elif endpoint == "stats":
            response =  requests.get(FIXTURES_STATS, headers=header, params=params)
        else:
            print("Endpoint is either fixtures or stats")

        return response.json, response.headers
    #run script for each league
