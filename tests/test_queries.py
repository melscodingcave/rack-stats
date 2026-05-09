from queries import (
    get_player_standings,
    get_tournament_summary,
    get_venue_stats,
    get_game_type_stats,
)
from database import Base, Tournament, Player, TournamentEntry, Match
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from datetime import date
import pytest
import sys
import os


# ─── Test Fixtures ────────────────────────────────────────────────


@pytest.fixture
def engine():
    """In-memory SQLite database for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def seeded_engine(engine):
    """Engine with known test data."""
    with Session(engine) as session:
        # Players
        diana = Player(name='Diana Prince', fargo_rate=575,
                       region='West Palm Beach, FL')
        clark = Player(name='Clark Kent', fargo_rate=463, region='Davie, FL')
        bruce = Player(name='Bruce Wayne', fargo_rate=620, region='Tampa, FL')
        session.add_all([diana, clark, bruce])
        session.commit()

        # Tournament
        t1 = Tournament(
            name='Shooters Monthly 9-Ball - January 2025',
            date=date(2025, 1, 15),
            location='Port St Lucie, FL',
            game_type='9-Ball',
            format='Double Elimination',
            payout=480.0,
        )
        t2 = Tournament(
            name='Beyond Billiards Open 9-Ball - February 2025',
            date=date(2025, 2, 10),
            location='Davie, FL',
            game_type='9-Ball',
            format='Single Elimination',
            payout=2400.0,
        )
        session.add_all([t1, t2])
        session.commit()

        # Tournament entries
        for player in [diana, clark, bruce]:
            session.add(TournamentEntry(
                tournament_id=t1.id, player_id=player.id))
        for player in [diana, clark]:
            session.add(TournamentEntry(
                tournament_id=t2.id, player_id=player.id))
        session.commit()

        # Matches — t1: Diana beats Clark, Diana beats Bruce
        session.add(Match(
            tournament_id=t1.id,
            player_one_id=diana.id,
            player_two_id=clark.id,
            winner_id=diana.id,
            player_one_racks_won=7,
            player_two_racks_won=3,
        ))
        session.add(Match(
            tournament_id=t1.id,
            player_one_id=diana.id,
            player_two_id=bruce.id,
            winner_id=diana.id,
            player_one_racks_won=7,
            player_two_racks_won=5,
        ))
        # t2: Clark beats Diana
        session.add(Match(
            tournament_id=t2.id,
            player_one_id=clark.id,
            player_two_id=diana.id,
            winner_id=clark.id,
            player_one_racks_won=7,
            player_two_racks_won=4,
        ))
        session.commit()

    return engine

# ─── Player Standings Tests ───────────────────────────────────────


def test_player_standings_win_count(seeded_engine):
    df = get_player_standings(seeded_engine)
    diana = df[df['name'] == 'Diana Prince'].iloc[0]
    assert diana['wins'] == 2


def test_player_standings_loss_count(seeded_engine):
    df = get_player_standings(seeded_engine)
    diana = df[df['name'] == 'Diana Prince'].iloc[0]
    assert diana['losses'] == 1


def test_player_standings_win_percentage(seeded_engine):
    df = get_player_standings(seeded_engine)
    diana = df[df['name'] == 'Diana Prince'].iloc[0]
    assert diana['win_pct'] == 66.67


def test_player_standings_rack_efficiency(seeded_engine):
    df = get_player_standings(seeded_engine)
    diana = df[df['name'] == 'Diana Prince'].iloc[0]
    assert diana['rack_efficiency'] == 54.55


def test_player_standings_sorted_by_wins(seeded_engine):
    df = get_player_standings(seeded_engine)
    assert df.iloc[0]['name'] == 'Diana Prince'


def test_player_with_no_matches_has_zero_wins(seeded_engine):
    df = get_player_standings(seeded_engine)
    bruce = df[df['name'] == 'Bruce Wayne'].iloc[0]
    assert bruce['wins'] == 0
    assert bruce['losses'] == 1

# ─── Tournament Summary Tests ─────────────────────────────────────


def test_tournament_summary_count(seeded_engine):
    df = get_tournament_summary(seeded_engine)
    assert len(df) == 2


def test_tournament_summary_field_size(seeded_engine):
    df = get_tournament_summary(seeded_engine)
    t1 = df[df['name'].str.contains('Shooters')].iloc[0]
    assert t1['field_size'] == 3


def test_tournament_summary_match_count(seeded_engine):
    df = get_tournament_summary(seeded_engine)
    t1 = df[df['name'].str.contains('Shooters')].iloc[0]
    assert t1['total_matches'] == 2


def test_tournament_summary_payout(seeded_engine):
    df = get_tournament_summary(seeded_engine)
    t2 = df[df['name'].str.contains('Beyond')].iloc[0]
    assert t2['payout'] == 2400.0

# ─── Venue Stats Tests ────────────────────────────────────────────


def test_venue_stats_total_payout(seeded_engine):
    df = get_venue_stats(seeded_engine)
    psl = df[df['location'] == 'Port St Lucie, FL'].iloc[0]
    assert psl['total_payout'] == 480.0


def test_venue_stats_unique_players(seeded_engine):
    df = get_venue_stats(seeded_engine)
    psl = df[df['location'] == 'Port St Lucie, FL'].iloc[0]
    assert psl['unique_players'] == 3

# ─── Game Type Stats Tests ────────────────────────────────────────


def test_game_type_stats_tournament_count(seeded_engine):
    df = get_game_type_stats(seeded_engine)
    nine_ball = df[df['game_type'] == '9-Ball'].iloc[0]
    assert nine_ball['tournaments'] == 2


def test_game_type_stats_total_matches(seeded_engine):
    df = get_game_type_stats(seeded_engine)
    nine_ball = df[df['game_type'] == '9-Ball'].iloc[0]
    assert nine_ball['total_matches'] == 3
