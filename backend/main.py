from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from notion_client import Client
from dotenv import load_dotenv
import os
import requests
from models import Content
from database import SessionLocal, engine, Base
from schemas import ContentRequest
from ai_engine import generate_content
from crud import save_content

# Load Environment Variables
load_dotenv()

# Notion Configuration
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

notion = Client(auth=NOTION_API_KEY)

try:
    Base.metadata.create_all(bind=engine)
except Exception as db_err:
    print(f"[Warning] Neon PostgreSQL connection failed at startup: {db_err}")

app = FastAPI()


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Content Repurposing Engine API Running"}


@app.post("/generate")
def generate(request: ContentRequest, db: Session = Depends(get_db)):

    # Generate AI Content
    generated = generate_content(
        request.content,
        request.platform,
        request.tone
    )

    # Save to Neon Database
    save_content(
        db,
        request.content,
        request.platform,
        request.tone,
        generated
    )

    # Save to Notion Database
    notion.pages.create(
        parent={
            "database_id": NOTION_DATABASE_ID
        },
        properties={
            "Platform": {
                "title": [
                    {
                        "text": {
                            "content": request.platform
                        }
                    }
                ]
            },

            "Tone": {
                "rich_text": [
                    {
                        "text": {
                            "content": request.tone
                        }
                    }
                ]
            },

            "Original Content": {
                "rich_text": [
                    {
                        "text": {
                            "content": request.content
                        }
                    }
                ]
            },

            "Generated Content": {
                "rich_text": [
                    {
                        "text": {
                            "content": generated
                        }
                    }
                ]
            }
        }
    )

    # Send to Zapier
    requests.post(
        "https://hooks.zapier.com/hooks/catch/27563844/4yzsq3s/",
        json={
            "platform": request.platform,
            "tone": request.tone,
            "original_content": request.content,
            "generated_content": generated
        }
    )

    return {
        "generated_content": generated
    }


@app.get("/history")
def get_history(db: Session = Depends(get_db)):

    history = db.query(Content).all()

    result = []

    for item in history:

        result.append({
            "id": item.id,
            "platform": item.platform,
            "tone": item.tone,
            "original_content": item.original_content,
            "generated_content": item.generated_content
        })

    return result


@app.delete("/delete/{content_id}")
def delete_content(content_id: int, db: Session = Depends(get_db)):

    content = db.query(Content).filter(
        Content.id == content_id
    ).first()

    if not content:
        return {"message": "Content not found"}

    db.delete(content)
    db.commit()

    return {"message": "Content deleted successfully"}