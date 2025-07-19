from pydantic import BaseModel, Field

class CheckinRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)

