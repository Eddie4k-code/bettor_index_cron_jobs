from email.mime import base
import logging
from db.db import get_db
from interfaces.odds_api_prop_history_interface import OddsAPIPropsHistoryInterface
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
from repositories.mlb_player_stats_repository import MLBPlayerStatsRepository
from pipelines.player_stats_pipeline import PlayerStatsPipeline
from repositories.hit_rate_event_queue_repository import HitRateEventQueueRepository
from repositories.odds_api_prop_history import OddsAPIPropsHistoryRepository
import argparse
from apis.ball_dont_lie_mlb_api import BallDontLieMlbAPI

load_dotenv()  # Load environment variables from .env file

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO


# --- CLI setup ---
def main():
    parser = argparse.ArgumentParser(description="Betting Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Props pipeline command
    props_parser = subparsers.add_parser("props", help="Run the props pipeline")
    props_parser.add_argument("--sport", type=str, default="basketball_nba", help="Sport key (default: basketball_nba)")
    props_parser.add_argument("--hours_ahead", type=int, default=24, help="Hours ahead to fetch props for (default: 24)")
    props_parser.add_argument("--markets", type=str, default="player_points", help="Markets to fetch (default: player_points)")

    # Teams pipeline command
    teams_parser = subparsers.add_parser("teams", help="Run the teams pipeline")
    teams_parser.add_argument("--sport", type=str, default="basketball_nba", help="Sport key (default: basketball_nba)")

    # Players pipeline command
    players_parser = subparsers.add_parser("players", help="Run the players pipeline")
    players_parser.add_argument("--sport", type=str, default="basketball_nba", help="Sport key (default: basketball_nba)")
    players_parser.add_argument("--season", type=int, default=2023, help="Season to fetch data for (default: 2023)")

    # Games pipeline command
    games_parser = subparsers.add_parser("games", help="Run the games pipeline")
    games_parser.add_argument("--sport", type=str, default="basketball_nba", help="Sport key (default: basketball_nba)")
    games_parser.add_argument("--season", type=int, default=2023, help="Season to fetch data for (default: 2023)")


    player_stats_parser = subparsers.add_parser("player_stats", help="Run the player stats pipeline")
    player_stats_parser.add_argument("--sport", type=str, default="basketball_nba",
                                        help="Sport key (default: basketball_nba)")
    player_stats_parser.add_argument("--season", type=int, default=2023,
                                        help="Season to fetch data for (default: 2023)")

    args = parser.parse_args()


    with get_db() as db:
        Base.metadata.create_all(db.get_bind())  # Ensure all tables are created
        
        """
        NBA
        """
        if args.sport == "basketball_nba":
            # Initalize repositories
            teams_repository = TeamsRepository(db)
            players_repository = PlayersRepository(db)
            games_repository = GamesRepository(db)
            nba_player_stats_repository = NBAPlayerStatsRepository(db)
            hit_rate_event_queue_repo = HitRateEventQueueRepository(db)
            odds_api_prop_history_repo = OddsAPIPropsHistoryRepository(db)
            props_repository = PropsRepository(db)
            # Initialize APIs
            http_client = HTTPXClient()
            api_config = APIConfig(api_key_env_var="THE_ODDS_API_KEY")
            the_odds_api = TheOddsAPI(api_config, http_client)
            sports_io_api = SportsIOAPI(APIConfig(api_key_env_var="SPORTS_IO_API_KEY"), http_client)
            # Initialize pipelines
            teams_pipeline = TeamsPipeline(teams_repository, sports_io_api)
            games_pipeline = GamesPipeline(games_repository, teams_repository, sports_io_api)
            players_pipeline = PlayersPipeline(teams_repository, players_repository, sports_io_api)
            props_pipeline = PropsPipeline(props_repository, the_odds_api, hit_rate_event_queue_repo, odds_api_prop_history_repo, teams_repository, players_repository)
            nba_player_stats_pipeline = PlayerStatsPipeline(
                sports_stats_api=sports_io_api,
                players_repository=players_repository,
                games_repository=games_repository,
                nba_player_stats_repository=nba_player_stats_repository,
            )
            # Run pipelines based on CLI command
            if args.command == "teams":
                teams_pipeline.get_teams(sport=args.sport)
            elif args.command == "games":
                games_pipeline.get_games(sport=args.sport, season=args.season)
            elif args.command == "players":
                players_pipeline.get_players(sport=args.sport, season=args.season)
            elif args.command == "props":
                props_pipeline.get_props(sport=args.sport, hours_ahead=args.hours_ahead, markets=args.markets.split(","))
            elif args.command == "player_stats":
                nba_player_stats_pipeline.get_player_stats(sport=args.sport, season=args.season)

        elif args.sport == "baseball_mlb":
            teams_repository = TeamsRepository(db)
            players_repository = PlayersRepository(db)
            games_repository = GamesRepository(db)
            mlb_player_stats_repository = MLBPlayerStatsRepository(db)
            hit_rate_event_queue_repo = HitRateEventQueueRepository(db)
            odds_api_prop_history_repo = OddsAPIPropsHistoryRepository(db)
            props_repository = PropsRepository(db)
            http_client = HTTPXClient()
            api_config = APIConfig(api_key_env_var="THE_ODDS_API_KEY")
            the_odds_api = TheOddsAPI(api_config, http_client)
            ball_dont_lie_api_mlb = BallDontLieMlbAPI(APIConfig(api_key_env_var="SPORTS_IO_API_KEY"), http_client)
            teams_pipeline = TeamsPipeline(teams_repository, ball_dont_lie_api_mlb)
            games_pipeline = GamesPipeline(games_repository, teams_repository, ball_dont_lie_api_mlb)
            players_pipeline = PlayersPipeline(teams_repository, players_repository, ball_dont_lie_api_mlb)
            props_pipeline = PropsPipeline(props_repository, the_odds_api, hit_rate_event_queue_repo, odds_api_prop_history_repo, teams_repository, players_repository)
            mlb_player_stats_pipeline = PlayerStatsPipeline(
                sports_stats_api=ball_dont_lie_api_mlb,
                players_repository=players_repository,
                games_repository=games_repository,
                mlb_player_stats_repository=mlb_player_stats_repository,
            )

            if args.command == "teams":
                teams_pipeline.get_teams(sport=args.sport)
            elif args.command == "games":
                games_pipeline.get_games(sport=args.sport, season=args.season)
            elif args.command == "players":
                players_pipeline.get_players(sport=args.sport, season=args.season)
            elif args.command == "props":
                props_pipeline.get_props(sport=args.sport, hours_ahead=args.hours_ahead, markets=args.markets.split(","))
            elif args.command == "player_stats":
                mlb_player_stats_pipeline.get_player_stats(sport=args.sport, season=args.season)
        else:
            logging.error(f"Unsupported sport: {args.sport}")
            exit(1)



if __name__ == "__main__":
    main()
