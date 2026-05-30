# from pydantic import BaseModel
# from typing import List

from pydantic import BaseModel
from typing import List


from typing import Optional, Union

class OddsAPIEvent(BaseModel):
    id: str
    sport_key: str
    sport_title: str
    commence_time: str
    home_team: str
    away_team: str

class OddsAPIOutcome(BaseModel):
    name: str
    price: Union[int, float]
    description: Optional[str] = None
    point: Optional[float] = None
    player_id: Optional[int] = None  # New field to link to player if applicable

class OddsAPIMarket(BaseModel):
    key: str
    last_update: str
    outcomes: List[OddsAPIOutcome]

class OddsAPIBookmaker(BaseModel):
    key: str
    title: str
    markets: List[OddsAPIMarket]

class OddsAPIProp(BaseModel):
    id: str
    sport_key: str
    sport_title: str
    commence_time: str
    home_team: str
    away_team: str
    bookmakers: List[OddsAPIBookmaker]