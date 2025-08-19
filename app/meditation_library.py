from nicegui import ui
from app.meditation_service import MeditationService
from app.models import MeditationType, DifficultyLevel
import logging

logger = logging.getLogger(__name__)


class MeditationLibrary:
    """Main interface for browsing and selecting meditation sessions"""

    def __init__(self):
        self.sessions = []
        self.filtered_sessions = []
        self.selected_type = None
        self.selected_difficulty = None

        # UI Components
        self.session_container = None
        self.no_results_label = None

    def create(self):
        """Create the meditation library interface"""
        # Apply calming theme
        ui.colors(
            primary="#3b82f6",
            secondary="#64748b",
            accent="#10b981",
            positive="#10b981",
            negative="#ef4444",
            warning="#f59e0b",
            info="#6366f1",
        )

        # Page styling
        ui.add_head_html("""
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Inter', system-ui, sans-serif;
            }
        </style>
        """)

        with ui.column().classes("w-full min-h-screen p-4"):
            # Header
            self._create_header()

            # Filters
            self._create_filters()

            # Sessions grid
            self._create_sessions_grid()

            # Load initial data
            self._load_sessions()

    def _create_header(self):
        """Create the page header"""
        with ui.card().classes("w-full max-w-6xl mx-auto p-8 bg-white/90 backdrop-blur shadow-xl rounded-2xl mb-6"):
            with ui.column().classes("items-center text-center"):
                ui.label("🧘‍♀️ Guided Meditation").classes("text-4xl font-bold text-gray-800 mb-2")
                ui.label("Find your inner peace through guided meditation sessions").classes(
                    "text-lg text-gray-600 mb-4 leading-relaxed"
                )
                ui.label("Choose from breathing exercises, mindfulness practices, and body scans").classes(
                    "text-base text-gray-500"
                )

    def _create_filters(self):
        """Create filter controls"""
        with ui.card().classes("w-full max-w-6xl mx-auto p-6 bg-white/80 backdrop-blur shadow-lg rounded-xl mb-6"):
            ui.label("Filter Sessions").classes("text-lg font-semibold text-gray-700 mb-4")

            with ui.row().classes("gap-6 items-end w-full"):
                # Type filter
                with ui.column().classes("flex-1"):
                    ui.label("Meditation Type").classes("text-sm font-medium text-gray-600 mb-2")
                    type_select = ui.select(
                        options={
                            None: "All Types",
                            MeditationType.BREATHING: "Breathing",
                            MeditationType.MINDFULNESS: "Mindfulness",
                            MeditationType.BODY_SCAN: "Body Scan",
                            MeditationType.LOVING_KINDNESS: "Loving Kindness",
                            MeditationType.CONCENTRATION: "Concentration",
                            MeditationType.WALKING: "Walking",
                            MeditationType.VISUALIZATION: "Visualization",
                        },
                        value=None,
                        on_change=lambda e: self._filter_by_type(e.value),
                    ).classes("w-full")

                # Difficulty filter
                with ui.column().classes("flex-1"):
                    ui.label("Difficulty Level").classes("text-sm font-medium text-gray-600 mb-2")
                    difficulty_select = ui.select(
                        options={
                            None: "All Levels",
                            DifficultyLevel.BEGINNER: "Beginner",
                            DifficultyLevel.INTERMEDIATE: "Intermediate",
                            DifficultyLevel.ADVANCED: "Advanced",
                        },
                        value=None,
                        on_change=lambda e: self._filter_by_difficulty(e.value),
                    ).classes("w-full")

                # Clear filters button
                ui.button(
                    "🔄 Clear Filters",
                    on_click=lambda: [
                        type_select.set_value(None),
                        difficulty_select.set_value(None),
                        self._clear_filters(),
                    ],
                ).classes("px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg")

    def _create_sessions_grid(self):
        """Create the sessions grid container"""
        with ui.card().classes("w-full max-w-6xl mx-auto p-6 bg-white/80 backdrop-blur shadow-lg rounded-xl"):
            ui.label("Available Sessions").classes("text-lg font-semibold text-gray-700 mb-4")

            # Container for session cards
            self.session_container = ui.column().classes("w-full gap-4")

            # No results message
            with self.session_container:
                self.no_results_label = ui.label("No sessions found. Try adjusting your filters.").classes(
                    "text-center text-gray-500 text-lg py-8 hidden"
                )

    def _load_sessions(self):
        """Load meditation sessions from the service"""
        try:
            self.sessions = MeditationService.get_active_sessions()
            if not self.sessions:
                # Create sample data if no sessions exist
                MeditationService.create_sample_data()
                self.sessions = MeditationService.get_active_sessions()

            self.filtered_sessions = self.sessions.copy()
            self._update_sessions_display()
        except Exception as e:
            logger.error(f"Error loading meditation sessions: {str(e)}", exc_info=True)
            ui.notify(f"Error loading sessions: {str(e)}", type="negative")

    def _filter_by_type(self, meditation_type):
        """Filter sessions by meditation type"""
        self.selected_type = meditation_type
        self._apply_filters()

    def _filter_by_difficulty(self, difficulty):
        """Filter sessions by difficulty level"""
        self.selected_difficulty = difficulty
        self._apply_filters()

    def _clear_filters(self):
        """Clear all filters"""
        self.selected_type = None
        self.selected_difficulty = None
        self._apply_filters()

    def _apply_filters(self):
        """Apply current filters to session list"""
        self.filtered_sessions = self.sessions.copy()

        if self.selected_type:
            self.filtered_sessions = [s for s in self.filtered_sessions if s.meditation_type == self.selected_type]

        if self.selected_difficulty:
            self.filtered_sessions = [
                s for s in self.filtered_sessions if s.difficulty_level == self.selected_difficulty
            ]

        self._update_sessions_display()

    def _update_sessions_display(self):
        """Update the sessions display"""
        if not self.session_container:
            return

        # Clear existing session cards
        self.session_container.clear()

        if not self.filtered_sessions:
            # Show no results message
            with self.session_container:
                ui.label("No sessions match your filters. Try adjusting your selection.").classes(
                    "text-center text-gray-500 text-lg py-8"
                )
            return

        # Create session cards
        with self.session_container:
            for session in self.filtered_sessions:
                self._create_session_card(session)

    def _create_session_card(self, session):
        """Create a card for a meditation session"""
        # Determine colors based on type
        type_colors = {
            MeditationType.BREATHING: "from-blue-400 to-blue-600",
            MeditationType.MINDFULNESS: "from-green-400 to-green-600",
            MeditationType.BODY_SCAN: "from-purple-400 to-purple-600",
            MeditationType.LOVING_KINDNESS: "from-pink-400 to-pink-600",
            MeditationType.CONCENTRATION: "from-indigo-400 to-indigo-600",
            MeditationType.WALKING: "from-yellow-400 to-yellow-600",
            MeditationType.VISUALIZATION: "from-teal-400 to-teal-600",
        }

        gradient = type_colors.get(session.meditation_type, "from-gray-400 to-gray-600")

        with ui.card().classes(
            "w-full p-6 bg-white shadow-lg hover:shadow-xl rounded-xl transition-shadow cursor-pointer border border-gray-100"
        ):
            with ui.row().classes("w-full items-start gap-4"):
                # Left side - gradient icon
                with ui.column().classes("items-center justify-center"):
                    ui.label("🧘‍♀️").style(
                        f"background: linear-gradient(135deg, {gradient.replace('from-', '#').replace(' to-', ', #')});"
                        "background-clip: text; -webkit-background-clip: text; color: transparent; font-size: 3rem;"
                    )

                # Main content
                with ui.column().classes("flex-1"):
                    # Title and description
                    ui.label(session.title).classes("text-xl font-bold text-gray-800 mb-1")
                    ui.label(session.description).classes("text-gray-600 mb-3 leading-relaxed")

                    # Metadata row
                    with ui.row().classes("gap-4 mb-4 items-center"):
                        # Duration
                        with ui.row().classes("items-center gap-1"):
                            ui.label("⏱️").classes("text-sm")
                            ui.label(f"{session.duration_minutes} min").classes("text-sm font-medium text-gray-700")

                        # Type
                        with ui.row().classes("items-center gap-1"):
                            ui.label("🎯").classes("text-sm")
                            ui.label(session.meditation_type.value.replace("_", " ").title()).classes(
                                "text-sm font-medium text-gray-700"
                            )

                        # Difficulty
                        with ui.row().classes("items-center gap-1"):
                            difficulty_icon = (
                                "⭐"
                                if session.difficulty_level == DifficultyLevel.BEGINNER
                                else "⭐⭐"
                                if session.difficulty_level == DifficultyLevel.INTERMEDIATE
                                else "⭐⭐⭐"
                            )
                            ui.label(difficulty_icon).classes("text-sm")
                            ui.label(session.difficulty_level.value.title()).classes(
                                "text-sm font-medium text-gray-700"
                            )

                    # Start button
                    ui.button(
                        "▶ Start Meditation",
                        on_click=lambda session_id=session.id: ui.navigate.to(f"/meditation/{session_id}"),
                    ).classes(
                        "px-6 py-2 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg shadow-md hover:shadow-lg transition-all font-medium"
                    )


def create():
    """Create the meditation library page"""

    @ui.page("/")
    def index():
        library = MeditationLibrary()
        library.create()
