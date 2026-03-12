from pydantic import BaseModel, Field
from typing import Optional

class UserProfileUpdate(BaseModel):
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0, description="CGPA (0 - 10)")
    interests: Optional[str] = Field(None, max_length=500, description="Comma separated interests")
