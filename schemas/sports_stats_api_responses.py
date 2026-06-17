from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


StringOrNumber = str | int | float

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


# --- BallDontLie MLB schemas ---

class BallDontLieMLBTeamSchema(BaseModel):
    id: int
    abbreviation: str
    display_name: str
    name: str
    location: str
    league: str
    division: str

class BallDontLieMLBTeamResponse(BaseModel):
    teams: List[BallDontLieMLBTeamSchema]

class BallDontLieMLBGameSchema(BaseModel):
    id: int
    season: int
    date: Optional[str] = None
    status: Optional[str] = None
    home_team_name: str
    home_team_id: int
    away_team_name: str
    away_team_id: int
    home_runs: Optional[int] = None
    away_runs: Optional[int] = None

class BallDontLieMLBGamesResponse(BaseModel):
    games: List[BallDontLieMLBGameSchema]

class BallDontLieMLBPlayerStatsSchema(BaseModel):
    player_id: int
    firstname: str
    lastname: str
    team_name: Optional[str] = None
    game_id: int
    season: int
    # Batting
    at_bats: Optional[int] = None
    hits: Optional[int] = None
    hr: Optional[int] = None
    rbi: Optional[int] = None
    bb: Optional[int] = None
    k: Optional[int] = None
    avg: Optional[StringOrNumber] = None
    obp: Optional[StringOrNumber] = None
    slg: Optional[StringOrNumber] = None
    doubles: Optional[int] = None
    triples: Optional[int] = None
    stolen_bases: Optional[int] = None
    plate_appearances: Optional[int] = None
    total_bases: Optional[int] = None
    # Pitching
    ip: Optional[StringOrNumber] = None
    p_k: Optional[int] = None
    p_bb: Optional[int] = None
    er: Optional[int] = None
    era: Optional[StringOrNumber] = None
    pitch_count: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    saves: Optional[int] = None
    games_started: Optional[int] = None

class BallDontLieMLBPlayerStatsResponse(BaseModel):
    stats: List[BallDontLieMLBPlayerStatsSchema]


class BallDontLieMLBInjuryTeamSchema(BaseModel):
    id: int
    slug: str
    abbreviation: str
    display_name: str
    short_display_name: str
    name: str
    location: str
    league: str
    division: str


class BallDontLieMLBInjuryPlayerSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    full_name: str
    debut_year: Optional[int] = None
    jersey: Optional[str] = None
    college: Optional[str] = None
    position: Optional[str] = None
    active: Optional[bool] = None
    birth_place: Optional[str] = None
    dob: Optional[str] = None
    age: Optional[int] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    draft: Optional[str] = None
    bats_throws: Optional[str] = None
    team: BallDontLieMLBInjuryTeamSchema


class BallDontLieMLBInjurySchema(BaseModel):
    player: BallDontLieMLBInjuryPlayerSchema
    date: Optional[str] = None
    return_date: Optional[str] = None
    type: Optional[str] = None
    detail: Optional[str] = None
    side: Optional[str] = None
    status: Optional[str] = None
    long_comment: Optional[str] = None
    short_comment: Optional[str] = None


class BallDontLieMLBInjuriesResponse(BaseModel):
    injuries: List[BallDontLieMLBInjurySchema]