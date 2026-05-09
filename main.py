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
from pipelines.teams_pipeline import TeamsPipeline
from apis.api_sports_io_api import SportsIOAPI
from repositories.teams_repository import TeamsRepository


load_dotenv()  # Load environment variables from .env file

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

def main():
    with get_db() as db:
        Base.metadata.create_all(db.get_bind())  # Create tables if they don't exist
        teams_repository = TeamsRepository(db)
        sports_stats_api_config = APIConfig(api_key_env_var="SPORTS_STATS_API_KEY")
        http_client = HTTPXClient()
        sports_stats_api = SportsIOAPI(sports_stats_api_config, http_client)  # Using SportsIOAPI for sports stats
        team_pipeline = TeamsPipeline(teams_repository, sports_stats_api)
        team_pipeline.get_teams(sport="basketball_nba")
main()
