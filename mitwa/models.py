from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Float
from sqlalchemy_utils import JSONType

from mitwa.db import Base


class VersionedEntity(Base):
    __tablename__: str = "versioned_entities"

    id: Column[str] = Column(String, primary_key=True)
    _versions: relationship = relationship("EntityVersion", back_populates="ref")


class EntityVersion(Base):
    __tablename__: str = "entity_versions"

    id: Column[str] = Column(String, primary_key=True)
    ref_id: Column[str] = Column(String, ForeignKey("versioned_entities.id"))
    timestamp: Column[float] = Column(Float)
    ref: relationship = relationship("VersionedEntity", back_populates="_versions")


class Ego(Base):
    __tablename__: str = "egos"

    id: Column[str] = Column(String, primary_key=True)
    name: Column[str] = Column(String)
    first_person_description: Column[str] = Column(String)
    second_person_description: Column[str] = Column(String, nullable=True)
    third_person_description: Column[str] = Column(String, nullable=True)


class EgoRef(Base):
    __tablename__: str = "ego_refs"

    id: Column[str] = Column(String, primary_key=True)
    ref_id: Column[str] = Column(String, ForeignKey("egos.id"))
    ref: relationship = relationship("Ego")


class Message(Base):
    __tablename__: str = "messages"

    id: Column[str] = Column(String, primary_key=True)
    author_id: Column[str] = Column(String, ForeignKey("egos.id"))
    content: Column[str] = Column(String)
    timestamp: Column[float] = Column(Float)


class Conversation(Base):
    __tablename__: str = "conversations"

    id: Column[str] = Column(String, primary_key=True)
    last_updated: Column[float] = Column(Float)
    participant_ids: relationship = relationship("EgoRef", back_populates="conversation")
    messages: relationship = relationship("Message", backref="conversation")


class EgoRef(Base):
    __tablename__: str = "ego_refs"

    id: Column[str] = Column(String, primary_key=True)
    conversation_id: Column[str] = Column(String, ForeignKey("conversations.id"))
    conversation: relationship = relationship(
        "Conversation", back_populates="participant_ids"
    )


class Analysis(Base):
    __tablename__: str = "analyses"

    id: Column[str] = Column(String, primary_key=True)
    conversation_id: Column[str] = Column(String, ForeignKey("conversations.id"))
    analyst_id: Column[str] = Column(String, ForeignKey("egos.id"))
    analysis: Column[str] = Column(String)
    conversation: relationship = relationship("Conversation", back_populates="analyses")
    analyst: relationship = relationship("Ego")


class User(Base):
    __tablename__: str = "users"

    id: Column[str] = Column(String, primary_key=True)
    supabase_uid: Column[str] = Column(String)
    name: Column[str] = Column(String)
    bio: Column[str] = Column(String)
    conversations: relationship = relationship("Conversation")
    analyses: relationship = relationship("Analysis")
    ego: relationship = relationship("Ego", uselist=False)
