"""
PostgreSQL database client using SQLAlchemy.
Manages database connection lifecycle and provides session management.
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import time

from app.core.config import settings


# ===================== SQLAlchemy Base =====================
Base = declarative_base()


# ===================== Database Engine =====================
class PostgresManager:
    """Manager class for PostgreSQL database operations."""
    
    def __init__(self):
        """Initialize PostgresManager with no engine."""
        self.engine = None
        self.SessionLocal = None
    
    def connect(self) -> bool:
        """Create database engine and session factory."""
        try:
            # Construct connection URL with psycopg2 dialect explicitly
            database_url = f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

            # Create engine with connection pooling
            self.engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,   # Recycle connections after 1 hour
                echo=settings.DEBUG,  # Log SQL queries in debug mode
                connect_args={
                    "connect_timeout": 10,  # 10 second timeout
                }
            )
            
            # Test connection with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    with self.engine.connect() as conn:
                        result = conn.execute(text("SELECT 1"))
                        print(f"✅ PostgreSQL connection test successful")
                        break
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Connection attempt {attempt + 1} failed, retrying...")
                        time.sleep(2)
                    else:
                        raise e
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            print("✅ Successfully connected to PostgreSQL database")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to PostgreSQL: {str(e)}")
            print("💡 Check logs: docker-compose logs postgres")
            self.engine = None
            self.SessionLocal = None
            return False
    
    def disconnect(self):
        """Close database engine and dispose of connection pool."""
        if self.engine is not None:
            try:
                self.engine.dispose()
                print("✅ PostgreSQL connection closed successfully")
            except Exception as e:
                print(f"⚠️ Error closing PostgreSQL connection: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if database engine is connected."""
        if self.engine is None:
            return False
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    def create_tables(self):
        """Create all database tables based on SQLAlchemy models."""
        if self.engine is None:
            print("⚠️ Cannot create tables: Database not connected")
            return
        
        try:
            # Import models to register them with Base
            from app.db import models
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            print("✅ Database tables created successfully")
            
        except Exception as e:
            print(f"⚠️ Error creating database tables: {str(e)}")
    
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session (dependency injection for FastAPI).
        
        Usage in FastAPI:
            @app.get("/endpoint")
            def endpoint(db: Session = Depends(get_db)):
                # Use db session
        
        Yields:
            Database session
        """
        if self.SessionLocal is None:
            raise Exception("Database not connected. Call connect() first.")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# ===================== Global Instance =====================
postgres_manager = PostgresManager()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    Usage:
        from app.db.postgres_client import get_db
        
        @router.post("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db here
    """
    return postgres_manager.get_session()
