from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL


Base = declarative_base()

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)



SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


def get_db_session():
    """
    Returns a database session.
    Use with context manager for automatic cleanup.
    
    Example:
        with get_db_session() as session:
            session.add(restaurant)
            session.commit()
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def init_db():
    """
    Create all tables defined in models.py
    Call this once to setup the database schema.
    """
    from . import models  
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def test_connection():
    """
    Test if database connection works.
    """
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    