from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Uuid, Boolean

Base = declarative_base()


class Node(Base):
    __tablename__ = 'node'

    id = Column(Integer, primary_key=True, autoincrement=True)
    node = Column(String(30))
    desc = Column(String(100))
    group = Column(String(30))
    type = Column(String(10))
    position = Column(Integer)
    uuid = Column(Uuid)
    puuid = Column(Uuid)
    expanded = Column(Boolean)


class Link(Base):
    __tablename__ = 'link'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(Uuid)
    node = Column(String(30))
    system = Column(String(30))
    client = Column(String(3))
    user = Column(String(20))
    password = Column(String(30))
    language = Column(String(2))


class Config(Base):
    __tablename__ = 'config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(30))
    value = Column(String(50))
