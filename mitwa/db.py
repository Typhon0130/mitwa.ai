from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String, Float
from sqlalchemy_utils import JSONType

# Create the SQLAlchemy engine and session
engine = create_engine("your_database_url")
Session = sessionmaker(bind=engine)

Base = declarative_base()

def init():

    # Create the database tables
    from mitwa.db import Base, engine


    Base.metadata.create_all(engine)

def seed():

    # TODO: create system Ego
