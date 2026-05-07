from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# Motorul async — conexiunea principală la baza de date
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,      # Verifică conexiunea înainte de fiecare query
    pool_size=10,            # Numărul de conexiuni simultane
    max_overflow=20,
)

# Factory pentru sesiuni async
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Obiectele rămân utilizabile după commit
    autoflush=False,
    autocommit=False,
)

# Clasa de bază pentru toate modelele


class Base(DeclarativeBase):
    pass

# Dependency FastAPI — yields sesiunea și o închide după request


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
