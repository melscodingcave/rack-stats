from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Session
import os

Base = declarative_base()


class Tournament(Base):
    __tablename__ = 'tournaments'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    location = Column(String, nullable=False)
    game_type = Column(String, nullable=False)
    format = Column(String, nullable=False)
    payout = Column(Float, nullable=False)

    entries = relationship('TournamentEntry', back_populates='tournament')
    matches = relationship('Match', back_populates='tournament')


class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    fargo_rate = Column(Integer, nullable=False)
    region = Column(String, nullable=False)

    entries = relationship('TournamentEntry', back_populates='player')


class TournamentEntry(Base):
    __tablename__ = 'tournament_entries'

    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey(
        'tournaments.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)

    tournament = relationship('Tournament', back_populates='entries')
    player = relationship('Player', back_populates='entries')


class Match(Base):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey(
        'tournaments.id'), nullable=False)
    player_one_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    player_two_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    winner_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    player_one_racks_won = Column(Integer, nullable=False)
    player_two_racks_won = Column(Integer, nullable=False)

    tournament = relationship('Tournament', back_populates='matches')
    player_one = relationship('Player', foreign_keys=[player_one_id])
    player_two = relationship('Player', foreign_keys=[player_two_id])
    winner = relationship('Player', foreign_keys=[winner_id])


def get_engine():
    # Always point to the data folder relative to this file's location
    db_path = os.path.join(os.path.dirname(__file__),
                           '..', 'data', 'rack_stats.db')
    return create_engine(f'sqlite:///{db_path}')


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    return Session(engine)
