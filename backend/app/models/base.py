import uuid
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, DateTime

db = SQLAlchemy()

def generate_uuid() -> str:
    """Generate a standard UUID4 hex string."""
    return str(uuid.uuid4())

class TimestampMixin:
    """Provides automatic created_at and updated_at UTC timestamps."""
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
