# 🎱 Rack Stats

A billiards tournament analytics pipeline for the Florida Billiards Circuit 2025.

Built as a portfolio project to demonstrate data engineering concepts: synthetic data generation, SQLite database modeling, SQL-based aggregations with SQLAlchemy, Pandas DataFrames, and interactive Streamlit dashboards.

---

## 🛠 Tech Stack

- **Language:** Python 3.13
- **Database:** SQLite via SQLAlchemy ORM
- **Data Processing:** Pandas
- **Visualization:** Plotly + Streamlit
- **Data:** Synthetic — generated via seeder script

---

## 📐 Data Model

| Table | Description |
|---|---|
| `tournaments` | 12 monthly tournaments across Florida venues |
| `players` | 32 Marvel/DC comic book players |
| `tournament_entries` | Many-to-many: players ↔ tournaments |
| `matches` | Match results with rack counts |

---

## 🚀 Getting Started

Install dependencies:
```bash
pip install -r requirements.txt
```

Generate the database:
```bash
python src/seed.py
```

Run the dashboard:
```bash
streamlit run src/app.py
```

---

## 📊 Dashboard Sections

- **Circuit Overview** — key metrics across all tournaments
- **Monthly Payout Trend** — open vs handicap tournament payouts over time
- **Player Standings** — win percentage and rack efficiency for top performers
- **Venue Analytics** — total payout by venue and game type
- **Game Type Breakdown** — tournament distribution and avg racks per match
- **Tournament Details** — full tournament table

---

## 🎱 Domain Notes

- **Handicap tournaments** — Fargo 650 and under, double elimination, $20-50 entry
- **Open tournaments** — Fargo 550-750, single elimination, $100-200 entry
- **Race lengths** — Race to 7 for 9/10-ball, race to 3 or 5 for Banks
- **Venues** — Backwoods Billiards (Okeechobee), Racks Billiards (Sanford), Diamond Billiards (Tampa), Beyond Billiards (Davie), Shooters Billiards (Port St Lucie), Village Cue Club (West Palm Beach)

---

## 🤖 AI-Assisted Development

See [AI-NOTES.md](./AI-NOTES.md) for a transparent log of how AI tooling was used in this project.