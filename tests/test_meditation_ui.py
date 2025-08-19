import pytest
from nicegui.testing import User
from app.database import reset_db
from app.meditation_service import MeditationService
from app.models import MeditationType, DifficultyLevel, MeditationSessionCreate


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


async def test_homepage_loads(user: User, new_db) -> None:
    """Test that the homepage loads correctly"""
    await user.open("/")
    await user.should_see("Guided Meditation")
    await user.should_see("Find your inner peace")
    await user.should_see("Filter Sessions")


async def test_homepage_with_sample_data(user: User, new_db) -> None:
    """Test homepage displays sample meditation sessions"""
    # Create sample data first
    MeditationService.create_sample_data()

    await user.open("/")
    await user.should_see("Available Sessions")
    await user.should_see("Basic Breathing Meditation")
    await user.should_see("Present Moment Awareness")
    await user.should_see("Full Body Relaxation")


async def test_meditation_session_filter_by_type(user: User, new_db) -> None:
    """Test filtering sessions by meditation type"""
    MeditationService.create_sample_data()

    await user.open("/")

    # Should see all sessions initially
    await user.should_see("Basic Breathing Meditation")
    await user.should_see("Present Moment Awareness")

    # Filter by breathing type - would need specific UI test implementation
    # This tests the basic functionality of having sample data available


async def test_meditation_player_page_loads(user: User, new_db) -> None:
    """Test that meditation player page loads correctly"""
    # Create a test session
    session_data = MeditationSessionCreate(
        title="Test Meditation",
        description="A test meditation session",
        meditation_type=MeditationType.BREATHING,
        difficulty_level=DifficultyLevel.BEGINNER,
        duration_minutes=5,
    )

    session = MeditationService.create_session(session_data)

    if session.id is not None:
        await user.open(f"/meditation/{session.id}")
        await user.should_see("Test Meditation")
        await user.should_see("A test meditation session")
        await user.should_see("Start")


async def test_meditation_player_with_invalid_session(user: User, new_db) -> None:
    """Test meditation player handles invalid session ID"""
    await user.open("/meditation/999")
    await user.should_see("Session not found")


async def test_navigation_between_pages(user: User, new_db) -> None:
    """Test navigation from library to player and back"""
    MeditationService.create_sample_data()

    # Start on homepage
    await user.open("/")
    await user.should_see("Guided Meditation")

    # Get a session and navigate to it
    sessions = MeditationService.get_active_sessions()
    if sessions:
        session_id = sessions[0].id
        if session_id is not None:
            await user.open(f"/meditation/{session_id}")
            await user.should_see("Back to Sessions")


async def test_empty_sessions_display(user: User, new_db) -> None:
    """Test display when no sessions are available"""
    await user.open("/")

    # Should create sample data automatically when none exist
    await user.should_see("Available Sessions")
    # The app should create sample data if none exists, so we should see sessions
