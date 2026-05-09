from database import get_engine
import sys
import os
import pandas as pd
from sqlalchemy import text
sys.path.insert(0, os.path.dirname(__file__))


def get_engine_instance():
    return get_engine()


def get_tournament_summary(engine) -> pd.DataFrame:
    query = text("""
        SELECT 
            t.id,
            t.name,
            t.date,
            t.location,
            t.game_type,
            t.format,
            t.payout,
            COUNT(DISTINCT te.player_id) as field_size,
            (SELECT COUNT(*) FROM matches m WHERE m.tournament_id = t.id) as total_matches
        FROM tournaments t
        LEFT JOIN tournament_entries te ON t.id = te.tournament_id
        GROUP BY t.id
        ORDER BY t.date
    """)
    return pd.read_sql(query, engine)


def get_player_standings(engine) -> pd.DataFrame:
    query = text("""
        SELECT
            p.id,
            p.name,
            p.fargo_rate,
            p.region,
            COUNT(DISTINCT te.tournament_id) as tournaments_played,
            SUM(CASE WHEN m.winner_id = p.id THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN m.winner_id != p.id THEN 1 ELSE 0 END) as losses,
            SUM(CASE WHEN m.player_one_id = p.id THEN m.player_one_racks_won
                     WHEN m.player_two_id = p.id THEN m.player_two_racks_won
                     ELSE 0 END) as total_racks_won,
            SUM(CASE WHEN m.player_one_id = p.id THEN m.player_two_racks_won
                     WHEN m.player_two_id = p.id THEN m.player_one_racks_won
                     ELSE 0 END) as total_racks_lost
        FROM players p
        LEFT JOIN tournament_entries te ON p.id = te.player_id
        LEFT JOIN matches m ON p.id IN (m.player_one_id, m.player_two_id)
            AND m.tournament_id = te.tournament_id
        GROUP BY p.id
        ORDER BY wins DESC, total_racks_won DESC
    """)
    df = pd.read_sql(query, engine)

    # Compute derived stats
    df['total_matches'] = df['wins'] + df['losses']
    df['win_pct'] = (df['wins'] / df['total_matches'] * 100).round(2)
    df['rack_efficiency'] = (
        df['total_racks_won'] /
        (df['total_racks_won'] + df['total_racks_lost']) * 100
    ).round(2)

    return df


def get_venue_stats(engine) -> pd.DataFrame:
    query = text("""
        SELECT
            t.location,
            t.game_type,
            COUNT(DISTINCT t.id) as tournaments_held,
            SUM(DISTINCT t.payout) as total_payout,
            AVG(DISTINCT t.payout) as avg_payout,
            COUNT(DISTINCT te.player_id) as unique_players
        FROM tournaments t
        LEFT JOIN tournament_entries te ON t.id = te.tournament_id
        GROUP BY t.location, t.game_type
        ORDER BY total_payout DESC
    """)
    return pd.read_sql(query, engine)


def get_game_type_stats(engine) -> pd.DataFrame:
    query = text("""
        SELECT
            t.game_type,
            COUNT(DISTINCT t.id) as tournaments,
            COUNT(m.id) as total_matches,
            AVG(t.payout) as avg_payout,
            AVG(m.player_one_racks_won + m.player_two_racks_won) as avg_racks_per_match
        FROM tournaments t
        LEFT JOIN matches m ON t.id = m.tournament_id
        GROUP BY t.game_type
        ORDER BY tournaments DESC
    """)
    return pd.read_sql(query, engine)


def get_monthly_payout_trend(engine) -> pd.DataFrame:
    query = text("""
        SELECT
            strftime('%Y-%m', date) as month,
            t.format,
            SUM(payout) as total_payout,
            COUNT(DISTINCT id) as tournament_count
        FROM tournaments t
        GROUP BY month, t.format
        ORDER BY month
    """)
    return pd.read_sql(query, engine)


def get_top_performers(engine, limit: int = 10) -> pd.DataFrame:
    df = get_player_standings(engine)
    return df[df['total_matches'] > 0].head(limit)
