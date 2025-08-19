import pytest
from app.database import reset_db
from app.meditation_service import MeditationService
from app.models import MeditationType, DifficultyLevel, MeditationSessionCreate, MeditationInstructionCreate


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


def test_create_session_with_maximum_duration(new_db):
    """Test creating session with maximum allowed duration"""
    session_data = MeditationSessionCreate(
        title="Long Meditation",
        description="A very long meditation session",
        meditation_type=MeditationType.CONCENTRATION,
        difficulty_level=DifficultyLevel.ADVANCED,
        duration_minutes=120,  # Maximum allowed
    )

    session = MeditationService.create_session(session_data)
    assert session.duration_minutes == 120


def test_create_session_with_minimum_duration(new_db):
    """Test creating session with minimum allowed duration"""
    session_data = MeditationSessionCreate(
        title="Quick Meditation",
        description="A very short meditation session",
        meditation_type=MeditationType.BREATHING,
        difficulty_level=DifficultyLevel.BEGINNER,
        duration_minutes=1,  # Minimum allowed
    )

    session = MeditationService.create_session(session_data)
    assert session.duration_minutes == 1


def test_instruction_with_zero_duration(new_db):
    """Test creating instruction with zero duration"""
    session_data = MeditationSessionCreate(
        title="Test Session",
        description="Test session for zero duration instruction",
        meditation_type=MeditationType.MINDFULNESS,
        difficulty_level=DifficultyLevel.BEGINNER,
        duration_minutes=5,
    )

    session = MeditationService.create_session(session_data)

    if session.id is not None:
        instruction_data = MeditationInstructionCreate(
            session_id=session.id,
            step_order=1,
            instruction_text="Instant instruction",
            duration_seconds=0,  # Zero duration
            is_pause=False,
        )

        instruction = MeditationService.add_instruction(instruction_data)
        assert instruction.duration_seconds == 0


def test_instruction_with_no_duration(new_db):
    """Test creating instruction with None duration"""
    session_data = MeditationSessionCreate(
        title="Test Session",
        description="Test session for null duration instruction",
        meditation_type=MeditationType.MINDFULNESS,
        difficulty_level=DifficultyLevel.BEGINNER,
        duration_minutes=5,
    )

    session = MeditationService.create_session(session_data)

    if session.id is not None:
        instruction_data = MeditationInstructionCreate(
            session_id=session.id,
            step_order=1,
            instruction_text="Untimed instruction",
            duration_seconds=None,  # No duration specified
            is_pause=False,
        )

        instruction = MeditationService.add_instruction(instruction_data)
        assert instruction.duration_seconds is None


def test_pause_instruction(new_db):
    """Test creating pause instruction"""
    session_data = MeditationSessionCreate(
        title="Test Session",
        description="Test session for pause instruction",
        meditation_type=MeditationType.BODY_SCAN,
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        duration_minutes=10,
    )

    session = MeditationService.create_session(session_data)

    if session.id is not None:
        instruction_data = MeditationInstructionCreate(
            session_id=session.id,
            step_order=1,
            instruction_text="Take a moment of silence",
            duration_seconds=60,
            is_pause=True,  # This is a pause instruction
        )

        instruction = MeditationService.add_instruction(instruction_data)
        assert instruction.is_pause


def test_instructions_ordered_correctly(new_db):
    """Test that instructions are returned in correct order"""
    session_data = MeditationSessionCreate(
        title="Ordered Session",
        description="Test session for instruction ordering",
        meditation_type=MeditationType.BREATHING,
        difficulty_level=DifficultyLevel.BEGINNER,
        duration_minutes=5,
    )

    session = MeditationService.create_session(session_data)

    if session.id is not None:
        # Add instructions in non-sequential order
        instruction_3 = MeditationInstructionCreate(
            session_id=session.id, step_order=3, instruction_text="Third instruction", duration_seconds=30
        )

        instruction_1 = MeditationInstructionCreate(
            session_id=session.id, step_order=1, instruction_text="First instruction", duration_seconds=30
        )

        instruction_2 = MeditationInstructionCreate(
            session_id=session.id, step_order=2, instruction_text="Second instruction", duration_seconds=30
        )

        # Add in reverse order
        MeditationService.add_instruction(instruction_3)
        MeditationService.add_instruction(instruction_1)
        MeditationService.add_instruction(instruction_2)

        # Retrieve session and check order
        retrieved_session = MeditationService.get_session_by_id(session.id)

        assert retrieved_session is not None
        assert len(retrieved_session.instructions) == 3
        assert retrieved_session.instructions[0].instruction_text == "First instruction"
        assert retrieved_session.instructions[1].instruction_text == "Second instruction"
        assert retrieved_session.instructions[2].instruction_text == "Third instruction"


def test_all_meditation_types_supported(new_db):
    """Test that all meditation types can be used"""
    for meditation_type in MeditationType:
        session_data = MeditationSessionCreate(
            title=f"{meditation_type.value} Meditation",
            description=f"Test {meditation_type.value} meditation",
            meditation_type=meditation_type,
            difficulty_level=DifficultyLevel.BEGINNER,
            duration_minutes=5,
        )

        session = MeditationService.create_session(session_data)
        assert session.meditation_type == meditation_type


def test_all_difficulty_levels_supported(new_db):
    """Test that all difficulty levels can be used"""
    for difficulty_level in DifficultyLevel:
        session_data = MeditationSessionCreate(
            title=f"{difficulty_level.value} Meditation",
            description=f"Test {difficulty_level.value} meditation",
            meditation_type=MeditationType.MINDFULNESS,
            difficulty_level=difficulty_level,
            duration_minutes=10,
        )

        session = MeditationService.create_session(session_data)
        assert session.difficulty_level == difficulty_level


def test_long_instruction_text(new_db):
    """Test instruction with very long text"""
    session_data = MeditationSessionCreate(
        title="Long Text Session",
        description="Test session for long instruction text",
        meditation_type=MeditationType.VISUALIZATION,
        difficulty_level=DifficultyLevel.ADVANCED,
        duration_minutes=15,
    )

    session = MeditationService.create_session(session_data)

    if session.id is not None:
        # Create a long instruction (near the 2000 character limit)
        long_text = "Imagine yourself in a peaceful meadow. " * 40  # About 1600 characters

        instruction_data = MeditationInstructionCreate(
            session_id=session.id, step_order=1, instruction_text=long_text, duration_seconds=300
        )

        instruction = MeditationService.add_instruction(instruction_data)
        assert len(instruction.instruction_text) > 1000
        assert instruction.instruction_text == long_text
