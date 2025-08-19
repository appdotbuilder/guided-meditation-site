from typing import List, Optional
from sqlmodel import select
from app.database import get_session
from app.models import (
    MeditationSession,
    MeditationInstruction,
    MeditationCategory,
    DifficultyLevel,
    MeditationType,
    MeditationSessionCreate,
    MeditationInstructionCreate,
)


class MeditationService:
    """Service layer for meditation session management"""

    @staticmethod
    def get_active_sessions() -> List[MeditationSession]:
        """Get all active meditation sessions"""
        with get_session() as session:
            statement = select(MeditationSession).where(MeditationSession.is_active)
            return list(session.exec(statement).all())

    @staticmethod
    def get_session_by_id(session_id: Optional[int]) -> Optional[MeditationSession]:
        """Get a meditation session by ID with instructions"""
        if session_id is None:
            return None

        with get_session() as session:
            meditation_session = session.get(MeditationSession, session_id)
            if meditation_session is None:
                return None

            # Explicitly load instructions to ensure they're available
            statement = (
                select(MeditationInstruction)
                .where(MeditationInstruction.session_id == session_id)
                .order_by("step_order")
            )
            instructions = list(session.exec(statement).all())
            meditation_session.instructions = instructions

            return meditation_session

    @staticmethod
    def get_sessions_by_type(meditation_type: MeditationType) -> List[MeditationSession]:
        """Get active sessions by meditation type"""
        with get_session() as session:
            statement = select(MeditationSession).where(
                MeditationSession.meditation_type == meditation_type, MeditationSession.is_active
            )
            return list(session.exec(statement).all())

    @staticmethod
    def get_sessions_by_difficulty(difficulty: DifficultyLevel) -> List[MeditationSession]:
        """Get active sessions by difficulty level"""
        with get_session() as session:
            statement = select(MeditationSession).where(
                MeditationSession.difficulty_level == difficulty, MeditationSession.is_active
            )
            return list(session.exec(statement).all())

    @staticmethod
    def create_session(session_data: MeditationSessionCreate) -> MeditationSession:
        """Create a new meditation session"""
        with get_session() as session:
            meditation_session = MeditationSession(
                title=session_data.title,
                description=session_data.description,
                meditation_type=session_data.meditation_type,
                difficulty_level=session_data.difficulty_level,
                duration_minutes=session_data.duration_minutes,
            )
            session.add(meditation_session)
            session.commit()
            session.refresh(meditation_session)
            return meditation_session

    @staticmethod
    def add_instruction(instruction_data: MeditationInstructionCreate) -> MeditationInstruction:
        """Add an instruction to a meditation session"""
        with get_session() as session:
            instruction = MeditationInstruction(
                session_id=instruction_data.session_id,
                step_order=instruction_data.step_order,
                instruction_text=instruction_data.instruction_text,
                duration_seconds=instruction_data.duration_seconds,
                is_pause=instruction_data.is_pause,
            )
            session.add(instruction)
            session.commit()
            session.refresh(instruction)
            return instruction

    @staticmethod
    def get_categories() -> List[MeditationCategory]:
        """Get all active meditation categories"""
        with get_session() as session:
            statement = select(MeditationCategory).where(MeditationCategory.is_active)
            return list(session.exec(statement).all())

    @staticmethod
    def create_sample_data():
        """Create sample meditation sessions for demonstration"""
        # Sample breathing meditation
        breathing_session = MeditationService.create_session(
            MeditationSessionCreate(
                title="Basic Breathing Meditation",
                description="A gentle introduction to meditation through focused breathing. Perfect for beginners.",
                meditation_type=MeditationType.BREATHING,
                difficulty_level=DifficultyLevel.BEGINNER,
                duration_minutes=10,
            )
        )

        # Add instructions for breathing meditation if session ID is available
        if breathing_session.id is None:
            return

        breathing_instructions = [
            (
                "Welcome to this 10-minute breathing meditation. Find a comfortable seated position and close your eyes.",
                30,
            ),
            ("Take a moment to notice your natural breath, without trying to change it. Simply observe.", 60),
            (
                "Now, begin to focus your attention on the sensation of breathing. Feel the air entering your nostrils.",
                90,
            ),
            ("As you breathe in, notice the expansion in your chest and belly. Breathe naturally and comfortably.", 90),
            (
                "When your mind wanders to other thoughts, gently return your attention to your breath. This is normal.",
                90,
            ),
            ("Continue focusing on each inhale and exhale. Let your breath be your anchor to the present moment.", 120),
            ("If you notice tension in your body, allow it to soften with each exhale.", 90),
            ("Keep bringing your attention back to your breathing whenever you notice it has wandered.", 120),
            ("Now, begin to deepen your breath slightly. Breathe in for 4 counts, hold for 2, exhale for 6.", 120),
            ("Continue this gentle rhythm. In for 4, hold for 2, out for 6.", 120),
            ("As we near the end, return to your natural breathing pattern.", 60),
            ("Take a moment to notice how you feel. Wiggle your fingers and toes, and when ready, open your eyes.", 45),
        ]

        for i, (instruction_text, duration) in enumerate(breathing_instructions, 1):
            MeditationService.add_instruction(
                MeditationInstructionCreate(
                    session_id=breathing_session.id,
                    step_order=i,
                    instruction_text=instruction_text,
                    duration_seconds=duration,
                    is_pause=False,
                )
            )

        # Sample mindfulness meditation
        mindfulness_session = MeditationService.create_session(
            MeditationSessionCreate(
                title="Present Moment Awareness",
                description="Cultivate awareness of the present moment through mindful observation.",
                meditation_type=MeditationType.MINDFULNESS,
                difficulty_level=DifficultyLevel.BEGINNER,
                duration_minutes=15,
            )
        )

        # Add instructions for mindfulness meditation if session ID is available
        if mindfulness_session.id is None:
            return

        mindfulness_instructions = [
            ("Welcome to this mindfulness meditation. Sit comfortably and allow your eyes to close gently.", 30),
            ("Begin by taking three slow, deep breaths to settle into this moment.", 45),
            ("Now, expand your awareness to include sounds around you. Don't judge or analyze, just notice.", 90),
            ("What sounds do you hear? Perhaps birds, traffic, or the hum of appliances. Simply observe.", 90),
            ("Now bring attention to physical sensations. Notice where your body touches the chair or floor.", 90),
            ("Feel the temperature of the air on your skin. Is there any tension or comfort in your body?", 90),
            ("Notice any emotions that might be present. Give them space without trying to change them.", 90),
            ("Observe your thoughts as they come and go, like clouds passing through the sky.", 120),
            ("You are the observer of your experience, not caught up in it. Rest in this awareness.", 120),
            ("If you find yourself getting carried away by thoughts, gently return to simply observing.", 90),
            ("Notice the quality of your mind right now. Is it busy, calm, scattered, or focused?", 90),
            ("Continue resting in open awareness, welcoming whatever arises in your experience.", 120),
            ("As we conclude, take a moment to appreciate this time you've given yourself.", 60),
            ("Slowly wiggle your fingers and toes, and when you're ready, gently open your eyes.", 45),
        ]

        for i, (instruction_text, duration) in enumerate(mindfulness_instructions, 1):
            MeditationService.add_instruction(
                MeditationInstructionCreate(
                    session_id=mindfulness_session.id,
                    step_order=i,
                    instruction_text=instruction_text,
                    duration_seconds=duration,
                    is_pause=False,
                )
            )

        # Sample body scan meditation
        bodyscan_session = MeditationService.create_session(
            MeditationSessionCreate(
                title="Full Body Relaxation",
                description="A soothing body scan meditation to release tension and promote deep relaxation.",
                meditation_type=MeditationType.BODY_SCAN,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                duration_minutes=20,
            )
        )

        # Add instructions for body scan meditation if session ID is available
        if bodyscan_session.id is None:
            return

        bodyscan_instructions = [
            ("Welcome to this body scan meditation. Lie down comfortably or sit with your back straight.", 30),
            ("Close your eyes and take several deep breaths to begin relaxing your entire body.", 60),
            ("Start by bringing attention to the top of your head. Notice any sensations there.", 75),
            ("Now move to your forehead. Allow any tension to soften and release.", 75),
            ("Notice your eyes, cheeks, and jaw. Let these muscles relax completely.", 75),
            ("Bring awareness to your neck and shoulders. Breathe into any areas of tension.", 90),
            ("Move down to your arms. Feel your upper arms, elbows, forearms, and hands relaxing.", 90),
            ("Focus on your chest area. Feel it rise and fall with each natural breath.", 90),
            ("Notice your upper back and shoulder blades. Allow them to settle and release.", 90),
            ("Bring attention to your abdomen. Let it be soft and relaxed.", 75),
            ("Move to your lower back. Breathe into this area and allow it to soften.", 90),
            ("Notice your hips and pelvis. Let any tightness dissolve with each exhale.", 90),
            ("Feel your thighs, both the front and back muscles. Allow them to be heavy and relaxed.", 90),
            ("Bring awareness to your knees, then your calves and shins.", 75),
            ("Finally, notice your ankles and feet. Feel them completely relaxed.", 75),
            ("Take a moment to feel your entire body as one unified, relaxed whole.", 90),
            ("Rest in this feeling of complete relaxation for a few moments.", 120),
            ("When you're ready, slowly wiggle your fingers and toes to reawaken your body.", 60),
            ("Take your time returning to full awareness, and gently open your eyes.", 45),
        ]

        for i, (instruction_text, duration) in enumerate(bodyscan_instructions, 1):
            MeditationService.add_instruction(
                MeditationInstructionCreate(
                    session_id=bodyscan_session.id,
                    step_order=i,
                    instruction_text=instruction_text,
                    duration_seconds=duration,
                    is_pause=False,
                )
            )
