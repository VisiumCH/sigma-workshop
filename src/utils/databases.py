"""Module with functions and queries to interact with the SQLite database."""

import sqlite3

DATABASE_PATH = "./data"


def create_tables():
    """Create the necessary tables."""
    conn = sqlite3.connect(f"{DATABASE_PATH}/agentic_fighters.db")
    cursor = conn.cursor()

    # Fighters table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fighters (
            name TEXT PRIMARY KEY,
            description TEXT,
            health INTEGER,
            strength INTEGER,
            speed INTEGER,
            agility INTEGER,
            intelligence INTEGER,
            armor INTEGER,
            level INTEGER,
            exp INTEGER,
            tiredness INTEGER
        )""")

    # Leaderboard table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            fighter TEXT PRIMARY KEY,
            latest_oponent TEXT,
            wins INTEGER,
            defeats INTEGER,
            draws INTEGER,
            score INTEGER,
            FOREIGN KEY (fighter) REFERENCES fighters(name)
        )""")

    conn.commit()


def add_fighter(fighter: dict):
    """Add a fighter to the fighters table, if there's no conflict.

    Args:
        fighter (dict): A dictionary with the fighter's information.
    """
    conn = sqlite3.connect(f"{DATABASE_PATH}/agentic_fighters.db")
    cursor = conn.cursor()

    query = f'''INSERT INTO fighters (name, description, health, strength, speed, agility, intelligence, armor, level, exp, tiredness)
        VALUES (
            "{fighter["name"]}",
            "{fighter["description"]}",
            {fighter["stats"]["health"]},
            {fighter["stats"]["strength"]},
            {fighter["stats"]["speed"]},
            {fighter["stats"]["agility"]},
            {fighter["stats"]["intelligence"]},
            {fighter["stats"]["armor"]},
            {fighter["stats"]["level"]},
            {fighter["stats"]["exp"]},
            {fighter["stats"]["tiredness"]}
        )
        ON CONFLICT (name) DO NOTHING'''

    cursor.execute(query)

    conn.commit()


def get_fighter_info(fighter_name: str) -> dict:
    """Get a fighter's information from the database.

    Args:
        fighter_name (str): The name of the fighter to retrieve information for.

    Returns:
        dict: A dictionary containing the fighter's information.
    """
    conn = sqlite3.connect(f"{DATABASE_PATH}/agentic_fighters.db")
    cursor = conn.cursor()

    cursor.execute(
        f'''SELECT name, description, health, strength, speed, agility, intelligence, armor, tiredness FROM fighters WHERE name = "{fighter_name}"'''
    )
    row = cursor.fetchone()
    if row:
        return {
            "name": row[0],
            "description": row[1],
            "health": row[2],
            "strength": row[3],
            "speed": row[4],
            "agility": row[5],
            "intelligence": row[6],
            "armor": row[7],
            "tiredness": row[8],
        }
    else:
        raise Exception(f"Fighter {fighter_name} not found!")


def update_leaderboard(winner: str, loser: str):
    """Update the leaderboard table with the winner and loser of a fight.

    Args:
        winner (str): The name of the winner of the fight.
        loser (str): The name of the loser of the fight.
    """
    conn = sqlite3.connect(f"{DATABASE_PATH}/agentic_fighters.db")
    cursor = conn.cursor()

    cursor.execute(f'''
        INSERT INTO leaderboard (fighter, latest_oponent, wins, defeats, draws, score)
        VALUES (
            "{winner}",
            "{loser}",
            1,
            0,
            0,
            3
        ) ON CONFLICT (fighter) DO UPDATE SET
            latest_oponent = excluded.latest_oponent,
            wins = wins + 1
        ''')

    cursor.execute(f'''
        INSERT INTO leaderboard (fighter, latest_oponent, wins, defeats, draws, score)
        VALUES (
            "{loser}",
            "{winner}",
            0,
            1,
            0,
            -2
        ) ON CONFLICT (fighter) DO UPDATE SET
            latest_oponent = excluded.latest_oponent,
            defeats = defeats + 1
        ''')

    conn.commit()


def update_scores():
    """_summary_"""
    conn = sqlite3.connect(f"{DATABASE_PATH}/agentic_fighters.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE leaderboard
        SET
            score = wins*3 - defeats*2 + draws
        """)

    conn.commit()


def add_exp_to_winner(winner: str, exp_gain=10):
    """Add exp to the winner of a fight.

    Args:
        winner (str): The name of the winner of the fight.
        exp_gain (int, optional): The amount of exp to add to the winner. Defaults to 10.
    """
    conn = sqlite3.connect(f"{DATABASE_PATH}/agentic_fighters.db")
    cursor = conn.cursor()

    cursor.execute(f'''
        UPDATE fighters
        SET
            exp = exp + {exp_gain}
        WHERE name = "{winner}"
        ''')
