import random
from datetime import date
from database import init_db, get_session, Tournament, Player, TournamentEntry, Match

VENUES = [
    {
        'name': 'Backwoods Billiards',
        'location': 'Okeechobee, FL',
        'allows_open': False,
    },
    {
        'name': 'Racks Billiards',
        'location': 'Sanford, FL',
        'allows_open': True,
    },
    {
        'name': 'Diamond Billiards',
        'location': 'Tampa, FL',
        'allows_open': True,
    },
    {
        'name': 'Beyond Billiards',
        'location': 'Davie, FL',
        'allows_open': True,
    },
    {
        'name': 'Shooters Billiards',
        'location': 'Port St Lucie, FL',
        'allows_open': False,
    },
    {
        'name': 'Village Cue Club',
        'location': 'West Palm Beach, FL',
        'allows_open': True,
    },
]

GAME_TYPES = ['9-Ball', '10-Ball', 'Banks']

PLAYER_NAMES = [
    # Marvel
    'Tony Stark', 'Steve Rogers', 'Natasha Romanoff', 'Bruce Banner',
    'Thor Odinson', 'Clint Barton', 'Peter Parker', 'Wanda Maximoff',
    'Sam Wilson', 'Bucky Barnes', 'Scott Lang', 'Carol Danvers',
    'T\'Challa', 'Stephen Strange', 'Peter Quill', 'Gamora',
    # DC
    'Bruce Wayne', 'Clark Kent', 'Diana Prince', 'Barry Allen',
    'Hal Jordan', 'Oliver Queen', 'Arthur Curry', 'Victor Stone',
    'John Constantine', 'Harley Quinn', 'Dinah Lance', 'Kara Danvers',
    'Dick Grayson', 'Barbara Gordon', 'Jason Todd', 'Tim Drake',
]


def get_race_length(game_type: str) -> int:
    if game_type == 'Banks':
        return random.choice([3, 5])
    return 7


def get_entry_fee(game_type: str, is_open: bool) -> int:
    if is_open:
        return random.randint(100, 200)
    if game_type == 'Banks':
        return random.randint(20, 50)
    return random.randint(20, 50)


def get_fargo_range(is_open: bool) -> tuple[int, int]:
    if is_open:
        return (550, 750)
    return (400, 650)


def generate_match_score(winner_race: int) -> tuple[int, int]:
    loser_score = random.randint(0, winner_race - 1)
    return winner_race, loser_score


def seed():
    engine = init_db()
    session = get_session(engine)

    # Clear existing data
    session.query(Match).delete()
    session.query(TournamentEntry).delete()
    session.query(Tournament).delete()
    session.query(Player).delete()
    session.commit()

    # Create players with varied Fargo ratings
    players = []
    for name in PLAYER_NAMES:
        player = Player(
            name=name,
            fargo_rate=random.randint(400, 750),
            region=random.choice([v['location'] for v in VENUES])
        )
        session.add(player)
        players.append(player)
    session.commit()

    # Create 12 monthly tournaments
    for month in range(1, 13):
        venue = random.choice(VENUES)
        game_type = random.choice(GAME_TYPES)
        is_open = venue['allows_open'] and random.choice([True, False])

        # Open tournaments = single elimination, handicap = double elimination
        format = 'Single Elimination' if is_open else 'Double Elimination'

        # Fargo range based on tournament type
        fargo_min, fargo_max = get_fargo_range(is_open)

        # Filter eligible players
        eligible = [p for p in players if fargo_min <=
                    p.fargo_rate <= fargo_max]

        # Field size weighted toward 22-24
        max_field = min(32, len(eligible))
        min_field = min(17, len(eligible))
        field_size = random.choices(
            population=list(range(min_field, max_field + 1)),
            weights=[
                3 if 22 <= i <= 24 else 1
                for i in range(min_field, max_field + 1)
            ],
            k=1
        )[0]

        entry_fee = get_entry_fee(game_type, is_open)

        tournament = Tournament(
            name=f'{venue["name"]} {"Open" if is_open else "Monthly"} {game_type} - {date(2025, month, 1).strftime("%B %Y")}',
            date=date(2025, month, random.randint(1, 28)),
            location=venue['location'],
            game_type=game_type,
            format=format,
            payout=field_size * entry_fee,
        )
        session.add(tournament)
        session.commit()

        # Enter random eligible field
        field = random.sample(eligible, field_size)
        for player in field:
            entry = TournamentEntry(
                tournament_id=tournament.id,
                player_id=player.id
            )
            session.add(entry)
        session.commit()

        # Generate matches
        race = get_race_length(game_type)
        remaining = field.copy()
        match_count = 0
        max_matches = field_size * 2

        while len(remaining) > 1 and match_count < max_matches:
            random.shuffle(remaining)
            next_round = []
            for i in range(0, len(remaining) - 1, 2):
                p1 = remaining[i]
                p2 = remaining[i + 1]
                winner = random.choice([p1, p2])
                loser = p2 if winner == p1 else p1

                w_racks, l_racks = generate_match_score(race)

                if winner == p1:
                    p1_racks, p2_racks = w_racks, l_racks
                else:
                    p1_racks, p2_racks = l_racks, w_racks

                match = Match(
                    tournament_id=tournament.id,
                    player_one_id=p1.id,
                    player_two_id=p2.id,
                    winner_id=winner.id,
                    player_one_racks_won=p1_racks,
                    player_two_racks_won=p2_racks,
                )
                session.add(match)
                next_round.append(winner)
                match_count += 1

            if len(remaining) % 2 == 1:
                next_round.append(remaining[-1])
            remaining = next_round

        session.commit()

    print(f"✅ Seeded 12 tournaments with {len(players)} players")
    print(f"   Marvel vs DC on the felt! 🎱")
    session.close()


if __name__ == '__main__':
    seed()
