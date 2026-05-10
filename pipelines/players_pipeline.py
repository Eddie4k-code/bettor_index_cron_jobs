from interfaces.players_pipeline_interface import PlayersPipelineInterface


class PlayersPipeline(PlayersPipelineInterface):
    def __init__(self, teams_repository, players_repository, api):
        self.teams_repository = teams_repository
        self.players_repository = players_repository
        self.api = api

    def get_players(self, sport: str, season: int):
        teams = self.teams_repository.get_teams(sport)
        for team in teams:
            players_response = self.api.get_players(team_id=team.id, season=season)
            for player_schema in players_response.players:
                player = self._map_schema_to_model(player_schema, team.id, sport)
                self.players_repository.insert_player(player)

    def _map_schema_to_model(self, player_schema, team_id, sport):
        from db.models.player import Player
        return Player(
            id=player_schema.id,
            first_name=player_schema.firstname,
            last_name=player_schema.lastname,
            team_id=team_id,
            sport_key=sport
        )