"""Application settings and configuration."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = Field(
        default="sqlite:///./inspector.db",
        description="Database connection URL"
    )
    
    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    
    # Debug and Development
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time in minutes"
    )
    
    # OpenAI
    openai_api_key: Optional[str] = Field(
        default=None, description="OpenAI API key for LLM summarization"
    )
    openai_model: str = Field(
        default="gpt-3.5-turbo", description="OpenAI model to use"
    )
    openai_base_url: str = Field(
        default="https://api.openai.com/v1", description="OpenAI API base URL"
    )
    
    # Monitoring
    monitoring_interval_minutes: int = Field(
        default=60, description="Interval between monitoring checks in minutes"
    )
    summary_frequency_hours: int = Field(
        default=24, description="How often to generate summaries in hours"
    )
    summary_time: str = Field(
        default="09:00", description="Time to generate summaries (HH:MM)"
    )
    
    # Social Media APIs
    linkedin_username: Optional[str] = Field(
        default=None, description="LinkedIn username for scraping"
    )
    linkedin_password: Optional[str] = Field(
        default=None, description="LinkedIn password for scraping"
    )
    github_token: Optional[str] = Field(
        default=None, description="GitHub personal access token"
    )
    
    # Notification
    email_enabled: bool = Field(default=False, description="Enable email notifications")
    email_smtp_server: Optional[str] = Field(
        default=None, description="SMTP server for email notifications"
    )
    email_smtp_port: int = Field(default=587, description="SMTP port")
    email_username: Optional[str] = Field(
        default=None, description="Email username"
    )
    email_password: Optional[str] = Field(
        default=None, description="Email password"
    )
    email_recipients: str = Field(
        default="", description="Comma-separated list of email recipients for reports"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(
        default=None, description="Log file path"
    )
    
    @property
    def email_recipients_list(self) -> list[str]:
        """Get email recipients as a list."""
        if not self.email_recipients:
            return []
        return [email.strip() for email in self.email_recipients.split(",") if email.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 