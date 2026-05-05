from email.mime import base
import logging
from db.db import get_db
from repositories.props_repository import PropsRepository
from pipelines.props_pipeline import PropsPipeline
from apis.the_odds_api import TheOddsAPI
from apis.api_config import APIConfig
from clients.httpx_client import HTTPXClient
import os
from dotenv import load_dotenv
from db.models.base import Base

load_dotenv()  # Load environment variables from .env file

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

def main():
    with get_db() as db:
        Base.metadata.create_all(db.get_bind())  # Create tables if they don't exist
        props_repository = PropsRepository(db)
        api_config = APIConfig(api_key_env_var="ODDS_API_KEY")
        http_client = HTTPXClient()
        the_odds_api = TheOddsAPI(api_config, http_client)
        props_pipeline = PropsPipeline(props_repository, the_odds_api)
        props_pipeline.get_props(24, sport="basketball_nba", markets="player_points")

main()
