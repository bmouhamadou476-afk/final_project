import os

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker
)


# ==============================================
# CHARGER LE FICHIER .env
# ==============================================

load_dotenv()


# ==============================================
# CONFIGURATION
# ==============================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:@localhost:3306/automatisation_reseau"
)


SQL_ECHO = (
    os.getenv(
        "SQL_ECHO",
        "False"
    ).lower()
    == "true"
)


# ==============================================
# SQLALCHEMY BASE
# ==============================================

class Base(DeclarativeBase):
    pass


# ==============================================
# ENGINE MYSQL
# ==============================================

engine = create_engine(

    DATABASE_URL,

    echo=SQL_ECHO,

    pool_pre_ping=True
)


# ==============================================
# SESSION DATABASE
# ==============================================

SessionLocal = sessionmaker(

    bind=engine,

    autoflush=False,

    autocommit=False
)


# ==============================================
# DEPENDANCE FASTAPI
# ==============================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()