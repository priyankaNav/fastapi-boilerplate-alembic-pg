from pydantic import BaseModel
from sqlalchemy import UUID

    
class ListFileInfo(BaseModel):
    file_id: str
    fileName: str
    class Config:
        orm_mode = True