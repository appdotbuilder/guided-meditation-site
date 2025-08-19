from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class MeditationType(str, Enum):
    BREATHING = "breathing"
    MINDFULNESS = "mindfulness"
    BODY_SCAN = "body_scan"
    LOVING_KINDNESS = "loving_kindness"
    CONCENTRATION = "concentration"
    WALKING = "walking"
    VISUALIZATION = "visualization"


# Persistent models (stored in database)
class MeditationSession(SQLModel, table=True):
    """A complete meditation session with metadata and instructions"""

    __tablename__ = "meditation_sessions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)
    description: str = Field(max_length=1000)
    meditation_type: MeditationType = Field(index=True)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER, index=True)
    duration_minutes: int = Field(gt=0, le=120)  # Duration between 1-120 minutes
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    instructions: List["MeditationInstruction"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "order_by": "MeditationInstruction.step_order"},
    )


class MeditationInstruction(SQLModel, table=True):
    """Individual instruction step within a meditation session"""

    __tablename__ = "meditation_instructions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="meditation_sessions.id", index=True)
    step_order: int = Field(ge=1)  # Order of the instruction step
    instruction_text: str = Field(max_length=2000)
    duration_seconds: Optional[int] = Field(default=None, ge=0)  # Optional timing for this step
    is_pause: bool = Field(default=False)  # Whether this is a silent pause step
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    session: MeditationSession = Relationship(back_populates="instructions")


class SessionCategoryLink(SQLModel, table=True):
    """Link table for many-to-many relationship between sessions and categories"""

    __tablename__ = "session_category_links"  # type: ignore[assignment]

    session_id: int = Field(foreign_key="meditation_sessions.id", primary_key=True)
    category_id: int = Field(foreign_key="meditation_categories.id", primary_key=True)


class MeditationCategory(SQLModel, table=True):
    """Categories to organize meditation sessions"""

    __tablename__ = "meditation_categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, index=True)
    description: str = Field(max_length=500)
    color_code: Optional[str] = Field(default=None, max_length=7, regex=r"^#[0-9A-Fa-f]{6}$")  # Hex color
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Many-to-many relationship with sessions
    sessions: List[MeditationSession] = Relationship(back_populates="categories", link_model=SessionCategoryLink)


# Add the relationship back to MeditationSession after all models are defined
MeditationSession.categories = Relationship(back_populates="sessions", link_model=SessionCategoryLink)


# Non-persistent schemas (for validation, forms, API requests/responses)
class MeditationSessionCreate(SQLModel, table=False):
    """Schema for creating a new meditation session"""

    title: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    meditation_type: MeditationType
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    duration_minutes: int = Field(gt=0, le=120)
    category_ids: Optional[List[int]] = Field(default=None)


class MeditationSessionUpdate(SQLModel, table=False):
    """Schema for updating an existing meditation session"""

    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    meditation_type: Optional[MeditationType] = Field(default=None)
    difficulty_level: Optional[DifficultyLevel] = Field(default=None)
    duration_minutes: Optional[int] = Field(default=None, gt=0, le=120)
    is_active: Optional[bool] = Field(default=None)
    category_ids: Optional[List[int]] = Field(default=None)


class MeditationInstructionCreate(SQLModel, table=False):
    """Schema for creating a new meditation instruction"""

    session_id: int
    step_order: int = Field(ge=1)
    instruction_text: str = Field(max_length=2000)
    duration_seconds: Optional[int] = Field(default=None, ge=0)
    is_pause: bool = Field(default=False)


class MeditationInstructionUpdate(SQLModel, table=False):
    """Schema for updating an existing meditation instruction"""

    step_order: Optional[int] = Field(default=None, ge=1)
    instruction_text: Optional[str] = Field(default=None, max_length=2000)
    duration_seconds: Optional[int] = Field(default=None, ge=0)
    is_pause: Optional[bool] = Field(default=None)


class MeditationCategoryCreate(SQLModel, table=False):
    """Schema for creating a new meditation category"""

    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    color_code: Optional[str] = Field(default=None, max_length=7, regex=r"^#[0-9A-Fa-f]{6}$")


class MeditationCategoryUpdate(SQLModel, table=False):
    """Schema for updating an existing meditation category"""

    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    color_code: Optional[str] = Field(default=None, max_length=7, regex=r"^#[0-9A-Fa-f]{6}$")
    is_active: Optional[bool] = Field(default=None)
