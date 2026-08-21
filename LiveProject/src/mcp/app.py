"""
    Used by uvicorn to run fastMCP, following instructions here 
    https://gofastmcp.com/deployment/http

"""

import pathlib
from fastmcp import FastMCP
import anyio
from typing import Any
import polars as pl
import os
from .base import mcp


####TOOLS

@mcp.tool
def load_dataframe(obj: list[dict[str, Any]]) -> pl.DataFrame:
    """Use polars to load a json for analysis"""
    pass


@mcp.tool
def load_visualization_tool():
    """Uses seaborn to aid visualization"""
    pass


####RESOURCES
@mcp.resource("gs://{year}")
def stats_data(year:str):
    """
        Exposes statistics for available seasons.
    """

    resources_path = os.getenv("RESOURCES_PATH")
    
    if resources_path.startswith("gs") or pathlib.Path(resources_path).exists():
        resources_url = resources_path # validate and think of how best to store this
    else:
        raise ValueError(
            "Path is invalid, function accepts only a google network storage object or a local path"
            )
    
    return resources_url

@mcp.resource("gs://{year}_fixtures")
def fixtures_data(year:str):
    """
        Exposes fixtures for available seasons.
    """

    resources_path = os.getenv("RESOURCES_PATH")
    
    if resources_path.startswith("gs") or pathlib.Path(resources_path).exists():
        fixtures_url = f"{resources_path}_fixtures"
    else:
        raise ValueError(
            "Path is invalid, function accepts only a google network storage object or a local path"
            )
    return fixtures_url

####PROMPTS
@mcp.prompt
def best_all_time_player():
    """
        Retrieves the best all-time player
    """

    return "VV"

app = mcp.http_app(path="/mcp")