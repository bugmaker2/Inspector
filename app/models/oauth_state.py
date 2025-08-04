"""OAuth state storage model."""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database.database import Base


class OAuthState(Base):
    """OAuth state storage for CSRF protection."""
    
    __tablename__ = "oauth_states"
    
    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    def is_expired(self) -> bool:
        """Check if the state token is expired."""
        return datetime.utcnow() > self.expires_at 