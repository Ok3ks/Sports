"""
    Used by uvicorn to run fastMCP, following instructions here 
    https://gofastmcp.com/deployment/http

"""

from typing import Any
import polars as pl
import os
from .base import mcp
from google.cloud import storage
from fastmcp.resources import ResourceContent


####TOOLS

@mcp.tool
def load_dataframe(obj: list[dict[str, Any]]) -> pl.DataFrame:
    """Use polars to load a json for analysis"""
    pass


@mcp.tool
def load_visualization_tool():
    """Uses seaborn to aid visualization"""
    pass

@mcp.tool
def extract_fixture():
    """Seperates stats and data """

####RESOURCES
@mcp.resource("data://{season}/")
def season_data(season:str):
    """
        Exposes all stats for an available seasons.
    """
    client = storage.Client(use_auth_w_custom_endpoint=False)
    bucket = client.get_bucket(season)
    blobs = bucket.list_blobs()
    blobs = [blob.download_as_text() for blob in blobs]
    return blobs

@mcp.resource("data://{season}/{gameweek}.json")
def gameweek_data(season:str, gameweek:str) -> tuple[dict[str, Any], dict[str,Any]]:
    """
        Exposes statistics for available specific gameweek, and specific fixture as a Tuple of text strings.

    """
    client = storage.Client()
    bucket = client.get_bucket(season)

    stats = bucket.get_blob(f"{gameweek}.json").download_as_text()
    fixture = bucket.get_blob(f"{gameweek}_fixture.json").download_as_text()

    return stats, fixture


####PROMPTS
@mcp.prompt
def best_all_time_player():
    """
        Retrieves the best all-time player
    """

    return "VV"

app = mcp.http_app(path="/mcp")