from datetime import datetime, timezone
import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from app.database import Base, SessionLocal, engine
from app.models import User, Profile, Game, GameRank, UserGame
from app.main import app
from app.seed import seed_games_and_ranks
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    seed_games_and_ranks()
    yield
    session = SessionLocal()
    try:
        session.query(UserGame).delete()
        session.query(Profile).delete()
        session.query(User).delete()
        session.query(GameRank).delete()
        session.query(Game).delete()
        session.commit()
    finally:
        session.close()


def test_automatic_table_creation_and_seeding_on_startup():
    with TestClient(app):
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        assert "users" in table_names
        assert "profiles" in table_names
        assert "games" in table_names
        assert "game_ranks" in table_names
        assert "user_games" in table_names

        db = SessionLocal()
        try:
            valorant = db.query(Game).filter(Game.name == "Valorant").first()
            assert valorant is not None
            assert len(valorant.ranks) == 25
            assert valorant.ranks[0].name == "Iron 1"
            assert valorant.ranks[0].value == 1
            assert valorant.ranks[-1].name == "Radiant"
            assert valorant.ranks[-1].value == 25

            pubg = db.query(Game).filter(Game.name == "PUBG").first()
            assert pubg is not None
            assert len(pubg.ranks) == 26
            assert pubg.ranks[0].name == "Bronze V"
            assert pubg.ranks[0].value == 1
            assert pubg.ranks[-1].name == "Master"
            assert pubg.ranks[-1].value == 26
        finally:
            db.close()


def test_user_lowercase_and_adult_fields():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        user = User(
            username="PixelWarrior",
            email="Pixel.Warrior@EXAMPLE.COM",
            hashed_password="hashed_pw_test",
            confirmed_adult=True,
            adult_confirmed_at=now,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.username == "pixelwarrior"
        assert user.email == "pixel.warrior@example.com"
        assert user.confirmed_adult is True
        assert user.adult_confirmed_at is not None
    finally:
        db.close()


def test_profile_structured_schedule_and_flags():
    db = SessionLocal()
    try:
        user = User(
            username="scheduler_pro",
            email="scheduler@example.com",
            hashed_password="hashed_secret",
            confirmed_adult=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        profile = Profile(
            user_id=user.id,
            display_name="Scheduler Pro",
            bio="Strategic player looking for coordinated teams.",
            timezone="UTC",
            language="en",
            mic=True,
            play_start_hour=19,
            play_end_hour=23,
            days_of_week="mon,wed,fri,sat",
        )
        db.add(profile)
        db.commit()
        db.refresh(user)

        assert user.profile.language == "en"
        assert user.profile.mic is True
        assert user.profile.play_start_hour == 19
        assert user.profile.play_end_hour == 23
        assert user.profile.days_of_week == "mon,wed,fri,sat"
    finally:
        db.close()


def test_user_game_with_rank_reference_and_constraints():
    db = SessionLocal()
    try:
        user = User(
            username="ranked_sniper",
            email="sniper@example.com",
            hashed_password="hashed_pw_test",
            confirmed_adult=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        valorant = db.query(Game).filter(Game.name == "Valorant").first()
        diamond_rank = db.query(GameRank).filter(
            GameRank.game_id == valorant.id,
            GameRank.name == "Diamond 2",
        ).first()

        user_game = UserGame(
            user_id=user.id,
            game_id=valorant.id,
            rank_id=diamond_rank.id,
            platform="PC",
            playstyle="competitive",
        )
        db.add(user_game)
        db.commit()
        db.refresh(user_game)

        assert user_game.platform == "PC"
        assert user_game.playstyle == "competitive"
        assert user_game.rank.name == "Diamond 2"
        assert user_game.rank.value == 17
        assert user_game.game.name == "Valorant"
    finally:
        db.close()
