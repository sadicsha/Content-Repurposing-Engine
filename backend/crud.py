from sqlalchemy.orm import Session
from models import Content


def save_content(db: Session, original, platform, tone, generated):

    db_content = Content(
        original_content=original,
        platform=platform,
        tone=tone,
        generated_content=generated
    )

    db.add(db_content)
    db.commit()
    db.refresh(db_content)

    return db_content