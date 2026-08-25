"""
    Used by uvicorn to run fastMCP, following instructions here 
    https://gofastmcp.com/deployment/http

"""

import json
from typing import Any
import polars as pl
from fastmcp.server import create_proxy

from .base import mcp
from google.cloud import storage
from typing import Annotated
from pydantic import Field

Season = Annotated[str, Field(pattern=r"^\d{4}[_]\d{4}$")]

####RESOURCES
@mcp.resource("fpl://{season}/{gameweek}.json")
def gameweek_data(season: Season, gameweek:str) -> tuple[dict[str, Any], dict[str,Any]]:
    """
        Exposes statistics for available specific gameweek, and specific fixture as a Tuple of text strings.

    """
    client = storage.Client()
    bucket = client.get_bucket(season)

    stats = bucket.get_blob(f"{gameweek}.json").download_as_text()
    fixture = bucket.get_blob(f"{gameweek}_fixture.json").download_as_text()

    return json.loads(stats), json.loads(fixture)


###TOOLS
@mcp.tool
async def read_resource(uri: str):
    """
        Read a resource from the MCP server by URI.
        
        Available resources are : 
        - "fpl://{season}/",
        - "fpl://{season}/{gameweek}.json"
        
    """

    content = await mcp.read_resource(uri)
    return content

@mcp.tool
def get_curr_event():
    pass


@mcp.tool
def get_live_data():
    pass


@mcp.tool
def load_dataframe(obj: list[dict[str, Any]]) -> pl.DataFrame:
    """Use polars to load a json for analysis"""
    df = pl.read_json(obj)
    return df


mcp.mount(create_proxy("https://mcp.pola.rs/mcp"), namespace="polars")

app = mcp.http_app(path="/mcp")
