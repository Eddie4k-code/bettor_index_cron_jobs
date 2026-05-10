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
from repositories.nba_player_stats_repository import NBAPlayerStatsRepository
from pipelines.player_stats_pipeline import PlayerStatsPipeline



load_dotenv()  # Load environment variables from .env file

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

def main():
    with get_db() as db:
        Base.metadata.create_all(db.get_bind())  # Create tables if they don't exist
        teams_repository = TeamsRepository(db)
        games_repository = GamesRepository(db)
        players_repository = PlayersRepository(db)
        nba_player_stats_repository = NBAPlayerStatsRepository(db)
        sports_stats_api_config = APIConfig(api_key_env_var="SPORTS_STATS_API_KEY")
        http_client = HTTPXClient()
        sports_stats_api = SportsIOAPI(sports_stats_api_config, http_client)  # Using SportsIOAPI for sports stats
        # --- Add this for game stats ---
        player_stats_pipeline = PlayerStatsPipeline(sports_stats_api=sports_stats_api, nba_player_stats_repository=nba_player_stats_repository, players_repository=players_repository)
        player_stats_pipeline.get_player_stats(sport="basketball_nba", season=2023)
main()
