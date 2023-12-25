#!/bin/bash

curl -X 'POST' \
  'http://127.0.0.1:8080/api/v1/league' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
   "gameweek_id": 16,
   "league_id": 85647
  }'