from sqlalchemy import Column, Integer, String, Text
from database import Base

class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    original_content = Column(Text)
    platform = Column(String)
    tone = Column(String)
    generated_content = Column(Text)