"""Database configuration and session management."""

import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from typing import Generator

from app.core.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()

# Create database engine with optimized connection pool
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=20,  # 增加连接池大小
    max_overflow=30,  # 增加最大溢出连接数
    pool_pre_ping=True,  # 连接前ping检查
    pool_recycle=3600,  # 1小时后回收连接
    pool_timeout=30,  # 连接超时时间
    echo=settings.debug,  # 调试模式下显示SQL
    echo_pool=settings.debug,  # 调试模式下显示连接池信息
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Database event listeners for monitoring
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance."""
    if "sqlite" in settings.database_url:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        cursor.execute("PRAGMA synchronous=NORMAL")  # 平衡性能和安全性
        cursor.execute("PRAGMA cache_size=10000")  # 增加缓存大小
        cursor.execute("PRAGMA temp_store=MEMORY")  # 临时表存储在内存
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB内存映射
        cursor.close()

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout events."""
    logger.debug(f"Database connection checked out: {connection_record.info}")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log connection checkin events."""
    logger.debug(f"Database connection checked in: {connection_record.info}")

def get_db() -> Generator[Session, None, None]:
    """Get database session with error handling."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database context error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    try:
        # Import models to ensure they are registered with Base
        from app.models.member import Member, Activity, Summary, SocialProfile
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def get_connection_pool_stats():
    """Get connection pool statistics."""
    pool = engine.pool
    stats = {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
    }
    
    # 只有某些连接池类型有invalid属性
    if hasattr(pool, 'invalid'):
        stats["invalid"] = pool.invalid()
    
    return stats

def health_check() -> dict:
    """Database health check."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        return {
            "status": "healthy",
            "pool_stats": get_connection_pool_stats()
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        } 