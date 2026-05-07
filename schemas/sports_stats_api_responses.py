from pydantic import BaseModel
from typing import Optional, List

class TeamSchema(BaseModel):
	id: int
	name: str
	nickname: str
	code: str
	city: str

class SportsStatsApiTeamResponse(BaseModel):
	teams: List[TeamSchema]
    