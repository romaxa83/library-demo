from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import Config

config = Config()

engine = create_engine(config.db.url, echo=True, pool_pre_ping=True, pool_size=10, max_overflow=20)  # Для отладки

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
