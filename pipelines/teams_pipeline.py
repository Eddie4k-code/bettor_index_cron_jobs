from interfaces.teams_pipeline_interface import TeamsPipelineInterface
from db.models.team import Team
from interfaces.teams_repository_interface import TeamsRepositoryInterface
from interfaces.sports_stats_api_interface import SportsStatsAPIInterface
import logging

logger = logging.getLogger(__name__)

class TeamsPipeline(TeamsPipelineInterface):
	def __init__(self, repository: TeamsRepositoryInterface, api: SportsStatsAPIInterface):
		self.repository = repository
		self.api = api

	def get_teams(self, sport: str) -> list[dict]:
		response = self.api.get_teams(sport)
		teams_data = response["teams"] if isinstance(response, dict) else getattr(response, "teams", [])
		logger.info(f"Fetched {len(teams_data)} teams from API")

		if sport == "basketball_nba":
			return self._process_nba_teams(teams_data, sport)

		if sport == "baseball_mlb":
			return self._process_mlb_teams(teams_data, sport)

		raise ValueError(f"Unsupported sport: {sport}")

	def _process_nba_teams(self, teams_data: list[dict], sport: str) -> list[dict]:
		result = []
		for team_schema in teams_data:
			team = Team(
				id = team_schema.id,
				name = team_schema.name.lower() if team_schema.name else "unknown",
				nickname = team_schema.nickname.lower() if team_schema.nickname else None,
				code = team_schema.code.lower() if team_schema.code else None,
				city = team_schema.city.lower() if team_schema.city else None,
				sport_key = sport.lower() if sport else None
			)
			self.repository.insert_team(team)
			logger.info(f"Inserted team: {team.name} (ID: {team.id})")
			result.append(self._dump_team_schema(team_schema))
		return result

	def _process_mlb_teams(self, teams_data: list[dict], sport: str) -> list[dict]:
		result = []
		for team_schema in teams_data:
			team = Team(
				id = team_schema.id,
				name = team_schema.name.lower() if team_schema.name else "unknown",
				nickname = team_schema.abbreviation.lower() if team_schema.abbreviation else None,
				code = team_schema.abbreviation.lower() if team_schema.abbreviation else None,
				city = team_schema.location.lower() if team_schema.location else None,
				sport_key = sport.lower() if sport else None
			)
			self.repository.insert_team(team)
			logger.info(f"Inserted team: {team.name} (ID: {team.id})")
			result.append(self._dump_team_schema(team_schema))
		return result

	def _dump_team_schema(self, team_schema):
		if hasattr(team_schema, "model_dump"):
			return team_schema.model_dump()

		return team_schema.dict()
