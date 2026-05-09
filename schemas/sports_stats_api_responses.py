from pydantic import BaseModel
from typing import Optional, List

class TeamSchema(BaseModel):
	id: int
	name: str
	nickname: str
	code: str
	city: Optional[str] = None

class SportsStatsApiTeamResponse(BaseModel):
	teams: List[TeamSchema]
    