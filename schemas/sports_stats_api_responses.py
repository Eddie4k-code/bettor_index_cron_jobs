from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TeamSchema(BaseModel):
	id: int
	name: str
	nickname: str
	code: str
	city: Optional[str] = None

class SportsStatsApiTeamResponse(BaseModel):
	teams: List[TeamSchema]
	
class GamesSchema(BaseModel):
	id: int
	season: int
	date: datetime
	status: str
	home_team: str
	home_team_id: int
	away_team: str
	away_team_id: int
	home_team_score: Optional[int] = None
	away_team_score: Optional[int] = None
	

class SportsStatsAPIGamesResponse(BaseModel):
    games: List[GamesSchema]
	

    