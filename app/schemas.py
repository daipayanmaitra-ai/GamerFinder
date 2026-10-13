"""Pydantic schemas for request validation and response serialization.

No feature schemas have been added yet. Future schemas (e.g., UserCreate,
UserResponse, GameFilter) will be defined here.
"""

from pydantic import BaseModel, ConfigDict


class HealthCheck(BaseModel):
    status: str
    project: str
    version: str

    model_config = ConfigDict(from_attributes=True)
