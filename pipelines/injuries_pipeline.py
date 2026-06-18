import logging
from datetime import datetime

from db.models.mlb_player_injuries import MLBPlayerInjuries
from interfaces.injuries_pipeline_interface import InjuriesPipelineInterface
from interfaces.player_injuries_repository_interface import PlayerInjuriesRepositoryInterface
from interfaces.sports_stats_api_interface import SportsStatsAPIInterface
from interfaces.teams_repository_interface import TeamsRepositoryInterface
from schemas.sports_stats_api_responses import BallDontLieMLBInjurySchema


logger = logging.getLogger(__name__)

class InjuriesPipeline(InjuriesPipelineInterface):
    def __init__(
        self,
        teams_repository: TeamsRepositoryInterface,
        player_injuries_repository: PlayerInjuriesRepositoryInterface,
        api: SportsStatsAPIInterface,
    ):
        self.teams_repository = teams_repository
        self.player_injuries_repository = player_injuries_repository
        self.api = api

    def get_injuries(self, sport: str) -> list[dict]:
        if sport != "baseball_mlb":
            raise ValueError(f"Unsupported sport: {sport}")

        teams = self.teams_repository.get_teams(sport)
        team_ids = [team.id for team in teams]

        if not team_ids:
            logger.info("No teams found for sport %s; skipping injuries fetch", sport)
            return []

        response = self.api.get_injuries(team_ids=team_ids)
        injuries = response.injuries if hasattr(response, "injuries") else []

        for injury in injuries:
            self.player_injuries_repository.insert_player_injury(
                self._map_mlb_injury_to_model(injury)
            )

        logger.info(
            "Processed %s MLB injuries across %s teams",
            len(injuries),
            len(team_ids),
        )
        return [injury.model_dump() for injury in injuries]

    def _map_mlb_injury_to_model(self, injury: BallDontLieMLBInjurySchema) -> MLBPlayerInjuries:
        return MLBPlayerInjuries(
            player_id=injury.player.id,
            team_id=injury.player.team.id,
            date=self._parse_datetime(injury.date),
            return_date=self._parse_datetime(injury.return_date),
            display_name=injury.player.full_name,
            position=injury.player.position,
            type=injury.type,
            detail=injury.detail,
            side=injury.side,
            status=injury.status,
            long_comment=injury.long_comment,
            short_comment=injury.short_comment,
        )

    def _parse_datetime(self, value: str | None) -> datetime | None:
        if value is None:
            return None

        normalized_value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized_value)