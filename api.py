"""
Building a REST API servicing a neural network checkpoint using FastAPI.
"""
import os
from os.path import join,realpath
from typing import List, Optional, Dict, Any

import urllib.request
from pathlib import Path

from fastapi import FastAPI
from fastapi import Request
from pydantic import BaseModel, Field

from src.report import LeagueWeeklyReport
from src.db import create_connection
from src.paths import BASE_DIR


class InferenceInput(BaseModel):
  r"""Input values for model inference. We will expect the image to be passed
  to us as a URL that we download """
  gameweek_id: int = Field(example = 12,
                           title = "Required gameweek ID"
                           )
  league_id: int = Field(example = 85647,
                         title = "Required League ID"
                         )
  
class InferenceResponse(BaseModel):
  r"""Output response for model inference."""
  error: bool = Field(..., example=False, title='error?')
  response: dict = Field(..., example={}, title='League response')

class ErrorResponse(BaseModel):
  r"""Error response for the API."""
  error: str = Field(..., example=True, title='error?')
  message: str = Field(..., example='', title='error message')
  traceback: Optional[str] = Field(None, example='', title='detailed traceback of the error')

app: FastAPI = FastAPI(
  title = 'League report',
  description = 'Connecting to league api')

@app.on_event("startup")
async def startup_event():
  r"""Initialize FastAPI."""

@app.post('/api/v1/league',
  response_model = InferenceResponse,
  responses = {422: {'model': ErrorResponse}, 500: {'model': ErrorResponse}})

#parse request and check cache

def predict(request: Request, body: InferenceInput, status_code = 200):
    print('`/api/v1/league` endpoint called.')

    test = LeagueWeeklyReport(int(body.gameweek_id), int(body.league_id))
    test.weekly_score_transformation()
    test.merge_league_weekly_transfer()
    test.add_auto_sub()

    output = test.create_report(display=True)
    return {'error':False,
    'response': output}