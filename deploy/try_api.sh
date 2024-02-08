#!/bin/bash

curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/league' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
   "gameweek_id": 21,
   "league_id": 85647
  }'