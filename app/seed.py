"""Seed initial game data and rank tiers for GamerFinder."""

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Game, GameRank

VALORANT_RANKS = [
    ("Iron 1", 1),
    ("Iron 2", 2),
    ("Iron 3", 3),
    ("Bronze 1", 4),
    ("Bronze 2", 5),
    ("Bronze 3", 6),
    ("Silver 1", 7),
    ("Silver 2", 8),
    ("Silver 3", 9),
    ("Gold 1", 10),
    ("Gold 2", 11),
    ("Gold 3", 12),
    ("Platinum 1", 13),
    ("Platinum 2", 14),
    ("Platinum 3", 15),
    ("Diamond 1", 16),
    ("Diamond 2", 17),
    ("Diamond 3", 18),
    ("Ascendant 1", 19),
    ("Ascendant 2", 20),
    ("Ascendant 3", 21),
    ("Immortal 1", 22),
    ("Immortal 2", 23),
    ("Immortal 3", 24),
    ("Radiant", 25),
]

PUBG_RANKS = [
    ("Bronze V", 1),
    ("Bronze IV", 2),
    ("Bronze III", 3),
    ("Bronze II", 4),
    ("Bronze I", 5),
    ("Silver V", 6),
    ("Silver IV", 7),
    ("Silver III", 8),
    ("Silver II", 9),
    ("Silver I", 10),
    ("Gold V", 11),
    ("Gold IV", 12),
    ("Gold III", 13),
    ("Gold II", 14),
    ("Gold I", 15),
    ("Platinum V", 16),
    ("Platinum IV", 17),
    ("Platinum III", 18),
    ("Platinum II", 19),
    ("Platinum I", 20),
    ("Diamond V", 21),
    ("Diamond IV", 22),
    ("Diamond III", 23),
    ("Diamond II", 24),
    ("Diamond I", 25),
    ("Master", 26),
]


def seed_games_and_ranks(db: Session = None) -> None:
    """Seed Valorant and PUBG with real rank tiers if not already present."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        games_to_seed = [
            ("Valorant", VALORANT_RANKS),
            ("PUBG", PUBG_RANKS),
        ]

        for game_name, ranks in games_to_seed:
            existing_game = db.query(Game).filter(Game.name == game_name).first()
            if not existing_game:
                game = Game(name=game_name)
                db.add(game)
                db.flush()  # populate game.id

                for rank_name, rank_value in ranks:
                    game_rank = GameRank(
                        game_id=game.id,
                        name=rank_name,
                        value=rank_value,
                    )
                    db.add(game_rank)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        if close_db:
            db.close()
