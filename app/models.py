"""SQLAlchemy database models for GamerFinder.

Defines the revised core entities: User, Profile, Game, GameRank, and UserGame.
"""

import enum
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship, validates

from app.database import Base


class Playstyle(str, enum.Enum):
    CASUAL = "casual"
    COMPETITIVE = "competitive"


class Platform(str, enum.Enum):
    PC = "PC"
    MOBILE = "Mobile"
    PLAYSTATION = "PlayStation"
    XBOX = "Xbox"


class User(Base):
    """User account model for authentication, identity, and age verification."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    confirmed_adult = Column(Boolean, default=False, nullable=False)
    adult_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    user_games = relationship("UserGame", back_populates="user", cascade="all, delete-orphan")

    @validates("username")
    def validate_username(self, key, value):
        if value is not None:
            return value.strip().lower()
        return value

    @validates("email")
    def validate_email(self, key, value):
        if value is not None:
            return value.strip().lower()
        return value

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', confirmed_adult={self.confirmed_adult})>"


class Profile(Base):
    """Gamer profile model containing bio, preferences, mic status, and structured schedule."""

    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    display_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    timezone = Column(String(50), nullable=True)
    language = Column(String(10), default="en", nullable=False)
    mic = Column(Boolean, default=False, nullable=False)
    play_start_hour = Column(Integer, nullable=True)  # 0 - 23 in user's timezone
    play_end_hour = Column(Integer, nullable=True)    # 0 - 23 in user's timezone
    days_of_week = Column(String(50), nullable=True)  # Comma-separated: e.g. 'mon,tue,wed,thu,fri,sat,sun'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "play_start_hour IS NULL OR (play_start_hour >= 0 AND play_start_hour <= 23)",
            name="check_play_start_hour_range",
        ),
        CheckConstraint(
            "play_end_hour IS NULL OR (play_end_hour >= 0 AND play_end_hour <= 23)",
            name="check_play_end_hour_range",
        ),
    )

    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        return f"<Profile(id={self.id}, user_id={self.user_id}, language='{self.language}', mic={self.mic})>"


class Game(Base):
    """Catalog of supported games."""

    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    ranks = relationship(
        "GameRank",
        back_populates="game",
        cascade="all, delete-orphan",
        order_by="GameRank.value",
    )
    user_games = relationship("UserGame", back_populates="game", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Game(id={self.id}, name='{self.name}')>"


class GameRank(Base):
    """Ordered ranks associated with a specific game."""

    __tablename__ = "game_ranks"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(
        Integer,
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(50), nullable=False)
    value = Column(Integer, nullable=False)  # Ordered numeric progression (e.g. Iron 1 = 1)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("game_id", "name", name="uq_game_rank_name"),
        UniqueConstraint("game_id", "value", name="uq_game_rank_value"),
    )

    # Relationships
    game = relationship("Game", back_populates="ranks")
    user_games = relationship("UserGame", back_populates="rank")

    def __repr__(self) -> str:
        return f"<GameRank(id={self.id}, game_id={self.game_id}, name='{self.name}', value={self.value})>"


class UserGame(Base):
    """Association linking a User to a Game with platform, structured rank, and playstyle."""

    __tablename__ = "user_games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    game_id = Column(
        Integer,
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rank_id = Column(
        Integer,
        ForeignKey("game_ranks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    platform = Column(String(50), nullable=False)
    playstyle = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "game_id", "platform", name="uq_user_game_platform"),
        CheckConstraint(
            "playstyle IN ('casual', 'competitive')",
            name="check_playstyle_valid",
        ),
        CheckConstraint(
            "platform IN ('PC', 'Mobile', 'PlayStation', 'Xbox')",
            name="check_platform_valid",
        ),
    )

    # Relationships
    user = relationship("User", back_populates="user_games")
    game = relationship("Game", back_populates="user_games")
    rank = relationship("GameRank", back_populates="user_games")

    def __repr__(self) -> str:
        return (
            f"<UserGame(id={self.id}, user_id={self.user_id}, game_id={self.game_id}, "
            f"platform='{self.platform}', playstyle='{self.playstyle}', rank_id={self.rank_id})>"
        )
