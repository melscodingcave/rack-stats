from queries import (
    get_tournament_summary,
    get_player_standings,
    get_venue_stats,
    get_game_type_stats,
    get_monthly_payout_trend,
    get_top_performers
)
from database import get_engine
import plotly.express as px
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))


st.set_page_config(
    page_title='🎱 Rack Stats',
    page_icon='🎱',
    layout='wide'
)

st.title('🎱 Rack Stats — Florida Billiards Circuit 2025')
st.markdown(
    'Tournament performance analytics for the Florida billiards community.')

engine = get_engine()

# ─── Overview Metrics ───────────────────────────────────────────
st.header('Circuit Overview')

tournaments = get_tournament_summary(engine)
players = get_player_standings(engine)

col1, col2, col3, col4 = st.columns(4)
col1.metric('Tournaments', len(tournaments))
col2.metric('Players', len(players))
col3.metric('Total Matches', tournaments['total_matches'].sum())
col4.metric('Total Payout', f"${tournaments['payout'].sum():,.0f}")

# ─── Monthly Payout Trend ────────────────────────────────────────
st.header('Monthly Payout Trend')

payout_trend = get_monthly_payout_trend(engine)
fig = px.bar(
    payout_trend,
    x='month',
    y='total_payout',
    color='format',
    title='Total Payout by Month and Format',
    labels={
        'total_payout': 'Total Payout ($)', 'month': 'Month', 'format': 'Format'},
    color_discrete_map={
        'Single Elimination': '#3B82F6',
        'Double Elimination': '#6B7280'
    }
)
st.plotly_chart(fig, use_container_width=True)

# ─── Player Standings ────────────────────────────────────────────
st.header('Player Standings')

top = get_top_performers(engine, limit=10)
fig2 = px.bar(
    top,
    x='name',
    y='win_pct',
    color='rack_efficiency',
    title='Top 10 Players by Win Percentage',
    labels={
        'name': 'Player',
        'win_pct': 'Win %',
        'rack_efficiency': 'Rack Efficiency %'
    },
    color_continuous_scale='Blues'
)
fig2.update_xaxes(tickangle=45)
st.plotly_chart(fig2, use_container_width=True)

# ─── Full Standings Table ────────────────────────────────────────
st.subheader('Full Standings')
display_cols = ['name', 'fargo_rate', 'tournaments_played',
                'wins', 'losses', 'win_pct', 'rack_efficiency']
st.dataframe(
    players[display_cols].rename(columns={
        'name': 'Player',
        'fargo_rate': 'Fargo',
        'tournaments_played': 'Events',
        'wins': 'W',
        'losses': 'L',
        'win_pct': 'Win %',
        'rack_efficiency': 'Rack Eff %'
    }),
    use_container_width=True
)

# ─── Venue Stats ────────────────────────────────────────────────
st.header('Venue Analytics')

venue = get_venue_stats(engine)
fig3 = px.bar(
    venue,
    x='location',
    y='total_payout',
    color='game_type',
    title='Total Payout by Venue and Game Type',
    labels={
        'location': 'Venue',
        'total_payout': 'Total Payout ($)',
        'game_type': 'Game Type'
    },
    color_discrete_map={
        '9-Ball': '#3B82F6',
        '10-Ball': '#1D4ED8',
        'Banks': '#6B7280'
    }
)
fig3.update_xaxes(tickangle=45)
st.plotly_chart(fig3, use_container_width=True)

# ─── Game Type Stats ────────────────────────────────────────────
st.header('Game Type Breakdown')

game_stats = get_game_type_stats(engine)
col1, col2 = st.columns(2)

with col1:
    fig4 = px.pie(
        game_stats,
        values='tournaments',
        names='game_type',
        title='Tournaments by Game Type',
        color_discrete_map={
            '9-Ball': '#3B82F6',
            '10-Ball': '#1D4ED8',
            'Banks': '#6B7280'
        }
    )
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    fig5 = px.bar(
        game_stats,
        x='game_type',
        y='avg_racks_per_match',
        title='Average Racks per Match by Game Type',
        labels={
            'game_type': 'Game Type',
            'avg_racks_per_match': 'Avg Racks per Match'
        },
        color='game_type',
        color_discrete_map={
            '9-Ball': '#3B82F6',
            '10-Ball': '#1D4ED8',
            'Banks': '#6B7280'
        }
    )
    st.plotly_chart(fig5, use_container_width=True)

# ─── Tournament Details ──────────────────────────────────────────
st.header('Tournament Details')
st.dataframe(
    tournaments[[
        'name', 'date', 'location', 'game_type',
        'format', 'field_size', 'total_matches', 'payout'
    ]].rename(columns={
        'name': 'Tournament',
        'date': 'Date',
        'location': 'Location',
        'game_type': 'Game Type',
        'format': 'Format',
        'field_size': 'Field',
        'total_matches': 'Matches',
        'payout': 'Payout ($)'
    }),
    use_container_width=True
)
