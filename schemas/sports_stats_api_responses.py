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
	

class PlayersSchema(BaseModel):
    id: int
    firstname: str
    lastname: str

class SportsStatsAPIPlayersResponse(BaseModel):
	players: List[PlayersSchema]   

class PlayerStatsSchemaNBA(BaseModel):
	player_id: int
	firstname: str
	lastname: str
	team_id: int
	game_id: int
	season: int
	min: Optional[str] = None
	points: Optional[int] = None
	pos: Optional[str] = None
	fgm: Optional[int] = None
	fga: Optional[int] = None
	fgp: Optional[str] = None
	ftm: Optional[int] = None
	fta: Optional[int] = None
	ftp: Optional[str] = None
	tpm: Optional[int] = None
	tpa: Optional[int] = None
	tpp: Optional[str] = None
	offReb: Optional[int] = None
	defReb: Optional[int] = None
	totReb: Optional[int] = None
	assists: Optional[int] = None
	pFouls: Optional[int] = None
	steals: Optional[int] = None
	turnovers: Optional[int] = None
	blocks: Optional[int] = None
	
	
	
class SportsStatsAPIPlayerStatsResponse(BaseModel):
    stats: List[PlayerStatsSchemaNBA]