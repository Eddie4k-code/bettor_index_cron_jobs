from email.mime import base
import logging
from db.db import get_db
from repositories.players_repository import PlayersRepository
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
from repositories.games_repository import GamesRepository
from pipelines.games_pipeline import GamesPipeline
from pipelines.players_pipeline import PlayersPipeline


load_dotenv()  # Load environment variables from .env file

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

def main():
    with get_db() as db:
        Base.metadata.create_all(db.get_bind())  # Create tables if they don't exist
        teams_repository = TeamsRepository(db)
        games_repository = GamesRepository(db)
        players_repository = PlayersRepository(db)
        sports_stats_api_config = APIConfig(api_key_env_var="SPORTS_STATS_API_KEY")
        http_client = HTTPXClient()
        sports_stats_api = SportsIOAPI(sports_stats_api_config, http_client)  # Using SportsIOAPI for sports stats
        players_pipeline = PlayersPipeline(teams_repository, players_repository=players_repository, api=sports_stats_api)
        players_pipeline.get_players(sport="basketball_nba", season=2023)  # Example: Fetch players for a specific season
main()
