import pytest
from app.database import reset_db
from app.meditation_service import MeditationService
from app.models import MeditationType, DifficultyLevel, MeditationSessionCreate, MeditationInstructionCreate


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


def test_create_session(new_db):
    """Test creating a new meditation session"""
    session_data = MeditationSessionCreate(
        title="Test Meditation",
        description="A test meditation session",
        meditation_type=MeditationType.BREATHING,
        difficulty_level=DifficultyLevel.BEGINNER,
        duration_minutes=5,
    )

    session = MeditationService.create_session(session_data)

    assert session.id is not None
    assert session.title == "Test Meditation"
    assert session.description == "A test meditation session"
    assert session.meditation_type == MeditationType.BREATHING
    assert session.difficulty_level == DifficultyLevel.BEGINNER
    assert session.duration_minutes == 5
    assert session.is_active


def test_get_session_by_id(new_db):
    """Test retrieving a session by ID"""
    session_data = MeditationSessionCreate(
        title="Test Session",
        description="Test description",
        meditation_type=MeditationType.MINDFULNESS,
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        duration_minutes=10,
    )

    created_session = MeditationService.create_session(session_data)
    session_id = created_session.id
    if session_id is not None:
        retrieved_session = MeditationService.get_session_by_id(session_id)
        assert retrieved_session is not None
        assert retrieved_session.id == created_session.id
        assert retrieved_session.title == "Test Session"


def test_get_session_by_id_none_input(new_db):
    """Test that get_session_by_id handles None input"""
    result = MeditationService.get_session_by_id(None)
    assert result is None


def test_get_session_by_id_nonexistent(new_db):
    """Test retrieving a non-existent session"""
    result = MeditationService.get_session_by_id(999)
    assert result is None


def test_get_active_sessions_empty(new_db):
    """Test getting active sessions when none exist"""
    sessions = MeditationService.get_active_sessions()
    assert sessions == []


def test_get_active_sessions_with_data(new_db):
    """Test getting active sessions with data"""
    session_data = MeditationSessionCreate(
        title="Active Session",
        description="An active session",
        meditation_type=MeditationType.BREATHING,
        difficulty_level=DifficultyLevel.BEGINNER,
        duration_minutes=5,
    )

    MeditationService.create_session(session_data)
    sessions = MeditationService.get_active_sessions()

    assert len(sessions) == 1
    assert sessions[0].title == "Active Session"
    assert sessions[0].is_active


def test_get_sessions_by_type(new_db):
    """Test filtering sessions by meditation type"""
    # Create sessions of different types
    breathing_data = MeditationSessionCreate(
        title="Breathing Session",
        description="Breathing meditation",
        meditation_type=MeditationType.BREATHING,
        difficulty_level=DifficultyLevel.BEGINNER,
        duration_minutes=5,
    )

    mindfulness_data = MeditationSessionCreate(
        title="Mindfulness Session",
        description="Mindfulness meditation",
        meditation_type=MeditationType.MINDFULNESS,
        difficulty_level=DifficultyLevel.BEGINNER,
        duration_minutes=10,
    )

    MeditationService.create_session(breathing_data)
    MeditationService.create_session(mindfulness_data)

    breathing_sessions = MeditationService.get_sessions_by_type(MeditationType.BREATHING)
    mindfulness_sessions = MeditationService.get_sessions_by_type(MeditationType.MINDFULNESS)

    assert len(breathing_sessions) == 1
    assert breathing_sessions[0].title == "Breathing Session"
    assert len(mindfulness_sessions) == 1
    assert mindfulness_sessions[0].title == "Mindfulness Session"


def test_get_sessions_by_difficulty(new_db):
    """Test filtering sessions by difficulty level"""
    beginner_data = MeditationSessionCreate(
        title="Beginner Session",
        description="Easy meditation",
        meditation_type=MeditationType.BREATHING,
        difficulty_level=DifficultyLevel.BEGINNER,
        duration_minutes=5,
    )

    advanced_data = MeditationSessionCreate(
        title="Advanced Session",
        description="Advanced meditation",
        meditation_type=MeditationType.CONCENTRATION,
        difficulty_level=DifficultyLevel.ADVANCED,
        duration_minutes=30,
    )

    MeditationService.create_session(beginner_data)
    MeditationService.create_session(advanced_data)

    beginner_sessions = MeditationService.get_sessions_by_difficulty(DifficultyLevel.BEGINNER)
    advanced_sessions = MeditationService.get_sessions_by_difficulty(DifficultyLevel.ADVANCED)

    assert len(beginner_sessions) == 1
    assert beginner_sessions[0].title == "Beginner Session"
    assert len(advanced_sessions) == 1
    assert advanced_sessions[0].title == "Advanced Session"


def test_add_instruction(new_db):
    """Test adding instructions to a meditation session"""
    session_data = MeditationSessionCreate(
        title="Test Session",
        description="Test session for instructions",
        meditation_type=MeditationType.BREATHING,
        difficulty_level=DifficultyLevel.BEGINNER,
        duration_minutes=5,
    )

    session = MeditationService.create_session(session_data)

    if session.id is not None:
        instruction_data = MeditationInstructionCreate(
            session_id=session.id,
            step_order=1,
            instruction_text="Take a deep breath",
            duration_seconds=30,
            is_pause=False,
        )

        instruction = MeditationService.add_instruction(instruction_data)

        assert instruction.id is not None
        assert instruction.session_id == session.id
        assert instruction.step_order == 1
        assert instruction.instruction_text == "Take a deep breath"
        assert instruction.duration_seconds == 30
        assert not instruction.is_pause


def test_session_with_instructions(new_db):
    """Test retrieving a session with its instructions"""
    session_data = MeditationSessionCreate(
        title="Session with Instructions",
        description="Test session",
        meditation_type=MeditationType.MINDFULNESS,
        difficulty_level=DifficultyLevel.BEGINNER,
        duration_minutes=5,
    )

    session = MeditationService.create_session(session_data)

    if session.id is not None:
        # Add multiple instructions
        instruction1_data = MeditationInstructionCreate(
            session_id=session.id, step_order=1, instruction_text="First instruction", duration_seconds=30
        )

        instruction2_data = MeditationInstructionCreate(
            session_id=session.id, step_order=2, instruction_text="Second instruction", duration_seconds=45
        )

        MeditationService.add_instruction(instruction1_data)
        MeditationService.add_instruction(instruction2_data)

        retrieved_session = MeditationService.get_session_by_id(session.id)

        assert retrieved_session is not None
        assert len(retrieved_session.instructions) == 2
        assert retrieved_session.instructions[0].step_order == 1
        assert retrieved_session.instructions[0].instruction_text == "First instruction"
        assert retrieved_session.instructions[1].step_order == 2
        assert retrieved_session.instructions[1].instruction_text == "Second instruction"


def test_create_sample_data(new_db):
    """Test creating sample meditation data"""
    MeditationService.create_sample_data()

    sessions = MeditationService.get_active_sessions()
    assert len(sessions) >= 3  # Should have at least breathing, mindfulness, and body scan

    # Check we have different types of sessions
    session_types = [session.meditation_type for session in sessions]
    assert MeditationType.BREATHING in session_types
    assert MeditationType.MINDFULNESS in session_types
    assert MeditationType.BODY_SCAN in session_types

    # Check that sessions have instructions
    for session in sessions:
        if session.id is not None:
            full_session = MeditationService.get_session_by_id(session.id)
            if full_session:
                assert len(full_session.instructions) > 0


def test_get_categories_empty(new_db):
    """Test getting categories when none exist"""
    categories = MeditationService.get_categories()
    assert categories == []
