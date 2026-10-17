# GamerFinder System Specification

## Overview

GamerFinder is an API service designed to connect gamers based on shared games, platforms, ranks, playstyles, and availability schedules.

---

## Database Entities & Schema (Revised)

### 1. `users` Table
Handles user account authentication, identity, and age verification.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `Integer` | PK, Autoincrement, Index | Unique user ID |
| `username` | `String(50)` | Unique, Index, Not Null | Unique handle (stored lowercased) |
| `email` | `String(255)` | Unique, Index, Not Null | Account email (stored lowercased) |
| `hashed_password` | `String(255)` | Not Null | Hashed password |
| `is_active` | `Boolean` | Not Null, Default `True` | Account status flag |
| `confirmed_adult` | `Boolean` | Not Null, Default `False` | Whether adult status (18+) is confirmed |
| `adult_confirmed_at` | `DateTime(tz)` | Nullable | Timestamp when adult status was confirmed |
| `created_at` | `DateTime(tz)` | Not Null, Server Default `now()` | Timestamp of registration |
| `updated_at` | `DateTime(tz)` | Not Null, Server Default `now()`, On Update `now()` | Timestamp of last update |

**Model Validation:**
- Lowercases `username` and `email` on assignment via `@validates`.

**Relationships:**
- `profile`: 1-to-1 relationship with `Profile` (`cascade="all, delete-orphan"`).
- `user_games`: 1-to-Many relationship with `UserGame` (`cascade="all, delete-orphan"`).

---

### 2. `profiles` Table
Stores gamer personal details, language, microphone availability, and structured play hours.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `Integer` | PK, Autoincrement, Index | Unique profile ID |
| `user_id` | `Integer` | FK(`users.id`, `ondelete="CASCADE"`), Unique, Index, Not Null | Associated user ID (1:1) |
| `display_name` | `String(100)` | Nullable | Public display name |
| `bio` | `Text` | Nullable | Player bio |
| `timezone` | `String(50)` | Nullable | Timezone string (e.g., `"UTC"`, `"America/New_York"`) |
| `language` | `String(10)` | Not Null, Default `"en"` | Primary language code (e.g., `"en"`) |
| `mic` | `Boolean` | Not Null, Default `False` | Voice mic available/used |
| `play_start_hour` | `Integer` | Nullable, Check `0 <= play_start_hour <= 23` | Start hour in profile's timezone |
| `play_end_hour` | `Integer` | Nullable, Check `0 <= play_end_hour <= 23` | End hour in profile's timezone |
| `days_of_week` | `String(50)` | Nullable | Comma-separated days (e.g., `"mon,tue,wed,thu,fri,sat,sun"`) |
| `created_at` | `DateTime(tz)` | Not Null, Server Default `now()` | Profile creation timestamp |
| `updated_at` | `DateTime(tz)` | Not Null, Server Default `now()`, On Update `now()` | Profile last update timestamp |

**Table Constraints:**
- `CheckConstraint("play_start_hour IS NULL OR (play_start_hour >= 0 AND play_start_hour <= 23)")`
- `CheckConstraint("play_end_hour IS NULL OR (play_end_hour >= 0 AND play_end_hour <= 23)")`

**Relationships:**
- `user`: Reference back to `User`.

---

### 3. `games` Table
Catalog of supported games.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `Integer` | PK, Autoincrement, Index | Unique game ID |
| `name` | `String(100)` | Unique, Index, Not Null | Game title (e.g., `"Valorant"`, `"PUBG"`) |
| `created_at` | `DateTime(tz)` | Not Null, Server Default `now()` | Date added |

**Relationships:**
- `ranks`: 1-to-Many relationship with `GameRank` (`cascade="all, delete-orphan"`, ordered by `value`).
- `user_games`: 1-to-Many relationship with `UserGame` (`cascade="all, delete-orphan"`).

---

### 4. `game_ranks` Table
Ordered numeric progression tiers for each game.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `Integer` | PK, Autoincrement, Index | Unique rank ID |
| `game_id` | `Integer` | FK(`games.id`, `ondelete="CASCADE"`), Index, Not Null | Associated game |
| `name` | `String(50)` | Not Null | Rank name (e.g., `"Iron 1"`, `"Radiant"`) |
| `value` | `Integer` | Not Null | Numeric ordering (e.g., 1 for lowest rank) |
| `created_at` | `DateTime(tz)` | Not Null, Server Default `now()` | Record creation timestamp |

**Table Constraints:**
- `UniqueConstraint("game_id", "name", name="uq_game_rank_name")`
- `UniqueConstraint("game_id", "value", name="uq_game_rank_value")`

**Relationships:**
- `game`: Reference back to `Game`.
- `user_games`: 1-to-Many relationship with `UserGame`.

---

### 5. `user_games` Table
Association linking users to games with platform, structured rank tier reference, and playstyle.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `Integer` | PK, Autoincrement, Index | Unique association ID |
| `user_id` | `Integer` | FK(`users.id`, `ondelete="CASCADE"`), Index, Not Null | Associated user |
| `game_id` | `Integer` | FK(`games.id`, `ondelete="CASCADE"`), Index, Not Null | Associated game |
| `rank_id` | `Integer` | FK(`game_ranks.id`, `ondelete="SET NULL"`), Index, Nullable | Associated ordered rank tier |
| `platform` | `String(50)` | Not Null, Check in `('PC', 'Mobile', 'PlayStation', 'Xbox')` | Gaming platform |
| `playstyle` | `String(50)` | Not Null, Check in `('casual', 'competitive')` | Player playstyle |
| `created_at` | `DateTime(tz)` | Not Null, Server Default `now()` | Association timestamp |
| `updated_at` | `DateTime(tz)` | Not Null, Server Default `now()`, On Update `now()` | Last update timestamp |

**Table Constraints:**
- `UniqueConstraint("user_id", "game_id", "platform", name="uq_user_game_platform")`
- `CheckConstraint("playstyle IN ('casual', 'competitive')", name="check_playstyle_valid")`
- `CheckConstraint("platform IN ('PC', 'Mobile', 'PlayStation', 'Xbox')", name="check_platform_valid")`

**Relationships:**
- `user`: Reference back to `User`.
- `game`: Reference back to `Game`.
- `rank`: Reference back to `GameRank`.

---

## Seed Data

Initial seeds on startup:
1. **Valorant**: 25 rank tiers (Iron 1 [1] to Radiant [25]).
2. **PUBG**: 26 rank tiers (Bronze V [1] to Master [26]).
