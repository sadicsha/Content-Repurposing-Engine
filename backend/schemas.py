from pydantic import BaseModel

class ContentRequest(BaseModel):
    content: str
    platform: str
    tone: str