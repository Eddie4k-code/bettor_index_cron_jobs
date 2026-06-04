from datetime import datetime
import logging

from db.models.mlb_player_stats import MLBPlayerStats
from db.models.nba_player_stats import NBAPlayerStats
from interfaces.games_repository_interface import GamesRepositoryInterface
from interfaces.mlb_player_stats_repository_interface import MLBPlayerStatsRepositoryInterface
from interfaces.nba_player_stats_repository_interface import NBAPlayerStatsRepositoryInterface
from interfaces.player_stats_pipeline_interface import PlayerStatsPipelineInterface
from interfaces.players_repository_interface import PlayersRepositoryInterface
from interfaces.sports_stats_api_interface import SportsStatsAPIInterface


logger = logging.getLogger(__name__)


class PlayerStatsPipeline(PlayerStatsPipelineInterface):
    def __init__(
        self,
        sports_stats_api: SportsStatsAPIInterface,
        players_repository: PlayersRepositoryInterface,
        games_repository: GamesRepositoryInterface,
        nba_player_stats_repository: NBAPlayerStatsRepositoryInterface | None = None,
        mlb_player_stats_repository: MLBPlayerStatsRepositoryInterface | None = None,
    ):
        self.sports_stats_api = sports_stats_api
        self.players_repository = players_repository
        self.games_repository = games_repository
        self.nba_player_stats_repository = nba_player_stats_repository
        self.mlb_player_stats_repository = mlb_player_stats_repository

    def get_player_stats(self, sport: str, season: int):
        if sport == "basketball_nba":
            self._process_nba_player_stats(sport=sport, season=season)
            return

        if sport == "baseball_mlb":
            self._process_mlb_player_stats(sport=sport, season=season)
            return

        raise ValueError(f"Unsupported sport: {sport}")

    def _process_nba_player_stats(self, sport: str, season: int):
        if self.nba_player_stats_repository is None:
            raise ValueError("NBA player stats repository is required for basketball_nba")

        players = self.players_repository.get_players(sport)

        for player in players:
            player_stats_response = self.sports_stats_api.get_player_stats(
                player_id=player.id,
                season=season,
                sport=sport,
            )

            for stat in player_stats_response.stats:
                game = self.games_repository.get_game(stat.game_id, sport)
                if game is None:
                    logger.warning(
                        "Game with ID %s not found for player ID %s. Skipping stats for this game.",
                        stat.game_id,
                        player.id,
                    )
                    continue

                logger.info(
                    "Processing NBA stats for player ID %s, season %s, game ID %s",
                    player.id,
                    stat.season,
                    stat.game_id,
                )

                self.nba_player_stats_repository.insert_player_stats(
                    player_stats=NBAPlayerStats(
                        player_id=player.id,
                        first_name=stat.firstname.lower() if stat.firstname else None,
                        last_name=stat.lastname.lower() if stat.lastname else None,
                        team_id=stat.team_id,
                        game_id=stat.game_id,
                        season=stat.season,
                        min=stat.min,
                        points=stat.points,
                        pos=stat.pos.lower() if stat.pos else None,
                        fgm=stat.fgm,
                        fga=stat.fga,
                        fgp=stat.fgp,
                        ftm=stat.ftm,
                        fta=stat.fta,
                        ftp=stat.ftp,
                        tpm=stat.tpm,
                        tpa=stat.tpa,
                        tpp=stat.tpp,
                        offReb=stat.offReb,
                        defReb=stat.defReb,
                        totReb=stat.totReb,
                        assists=stat.assists,
                        pFouls=stat.pFouls,
                        steals=stat.steals,
                        turnovers=stat.turnovers,
                        blocks=stat.blocks,
                        sport_key=sport,
                        commence_time=self._normalize_game_date(game.date),
                    )
                )

    def _process_mlb_player_stats(self, sport: str, season: int):
        if self.mlb_player_stats_repository is None:
            raise ValueError("MLB player stats repository is required for baseball_mlb")

        players = self.players_repository.get_players(sport)

        for player in players:
            player_stats_response = self.sports_stats_api.get_player_stats(
                player_id=player.id,
                season=season,
                sport=sport,
            )

            for stat in player_stats_response.stats:
                game = self.games_repository.get_game(stat.game_id, sport)
                if game is None:
                    logger.warning(
                        "Game with ID %s not found for player ID %s. Skipping stats for this game.",
                        stat.game_id,
                        player.id,
                    )
                    continue

                logger.info(
                    "Processing MLB stats for player ID %s, season %s, game ID %s",
                    player.id,
                    stat.season,
                    stat.game_id,
                )

                self.mlb_player_stats_repository.insert_player_stats(
                    player_stats=MLBPlayerStats(
                        player_id=player.id,
                        first_name=stat.firstname.lower() if stat.firstname else None,
                        last_name=stat.lastname.lower() if stat.lastname else None,
                        team_name=stat.team_name.lower() if stat.team_name else None,
                        game_id=stat.game_id,
                        season=stat.season,
                        at_bats=stat.at_bats,
                        hits=stat.hits,
                        hr=stat.hr,
                        rbi=stat.rbi,
                        bb=stat.bb,
                        k=stat.k,
                        avg=stat.avg,
                        obp=stat.obp,
                        slg=stat.slg,
                        doubles=stat.doubles,
                        triples=stat.triples,
                        stolen_bases=stat.stolen_bases,
                        plate_appearances=stat.plate_appearances,
                        total_bases=stat.total_bases,
                        ip=stat.ip,
                        p_k=stat.p_k,
                        p_bb=stat.p_bb,
                        er=stat.er,
                        era=stat.era,
                        pitch_count=stat.pitch_count,
                        wins=stat.wins,
                        losses=stat.losses,
                        saves=stat.saves,
                        games_started=stat.games_started,
                        sport_key=sport,
                        commence_time=self._normalize_game_date(game.date),
                    )
                )

    def _normalize_game_date(self, value):
        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))

        return value

