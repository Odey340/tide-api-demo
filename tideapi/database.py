from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Use absolute path to load .env reliably
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

# Now load the database URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
print("Connecting to DB:", SQLALCHEMY_DATABASE_URL)

if SQLALCHEMY_DATABASE_URL is None:
    raise Exception("DATABASE_URL not found. Check your .env file and load_dotenv()")

# Setup the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()