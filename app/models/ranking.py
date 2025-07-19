from pydantic import BaseModel
from typing import List

class RankingEntry(BaseModel):
    username: str
    points: int

class WeeklyRankingResponse(BaseModel):
    week_id: str
    ranking: List[RankingEntry]