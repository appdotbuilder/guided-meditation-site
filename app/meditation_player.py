from typing import Optional
from nicegui import ui
from app.meditation_service import MeditationService
from app.models import MeditationSession


class MeditationPlayer:
    """Component for playing meditation sessions with guided instructions"""

    def __init__(self, session_id: int):
        self.session_id = session_id
        self.session: Optional[MeditationSession] = None
        self.current_step = 0
        self.is_playing = False
        self.is_paused = False
        self.timer: Optional[ui.timer] = None

        # UI Components
        self.instruction_label: Optional[ui.label] = None
        self.progress_bar: Optional[ui.linear_progress] = None
        self.time_label: Optional[ui.label] = None
        self.play_button: Optional[ui.button] = None
        self.step_info_label: Optional[ui.label] = None

        # Load the session
        self._load_session()

    def _load_session(self):
        """Load the meditation session from the database"""
        self.session = MeditationService.get_session_by_id(self.session_id)
        if self.session is None:
            ui.notify("Meditation session not found", type="negative")
            return

    def create(self):
        """Create the meditation player UI"""
        if self.session is None:
            ui.label("Session not found").classes("text-red-500 text-center text-lg")
            return

        # Header section with calming design
        with ui.card().classes(
            "w-full max-w-4xl mx-auto p-8 bg-gradient-to-br from-blue-50 to-indigo-100 shadow-lg rounded-xl"
        ):
            # Session title and info
            ui.label(self.session.title).classes("text-3xl font-bold text-center text-gray-800 mb-2")
            ui.label(self.session.description).classes("text-lg text-center text-gray-600 mb-4 leading-relaxed")

            # Session metadata
            with ui.row().classes("justify-center gap-6 mb-6"):
                with ui.column().classes("items-center"):
                    ui.label("Duration").classes("text-sm text-gray-500 uppercase tracking-wider")
                    ui.label(f"{self.session.duration_minutes} min").classes("text-lg font-semibold text-gray-700")

                with ui.column().classes("items-center"):
                    ui.label("Type").classes("text-sm text-gray-500 uppercase tracking-wider")
                    ui.label(self.session.meditation_type.value.replace("_", " ").title()).classes(
                        "text-lg font-semibold text-gray-700"
                    )

                with ui.column().classes("items-center"):
                    ui.label("Level").classes("text-sm text-gray-500 uppercase tracking-wider")
                    ui.label(self.session.difficulty_level.value.title()).classes("text-lg font-semibold text-gray-700")

        # Main meditation interface
        with ui.card().classes("w-full max-w-4xl mx-auto mt-6 p-8 bg-white shadow-lg rounded-xl"):
            # Current instruction display
            self.instruction_label = ui.label("Click play to begin your meditation journey").classes(
                "text-xl text-center text-gray-700 mb-8 leading-relaxed min-h-24 flex items-center justify-center p-4 bg-gray-50 rounded-lg"
            )

            # Progress indicators
            with ui.column().classes("w-full mb-8"):
                self.progress_bar = ui.linear_progress(value=0, show_value=False).classes("w-full h-2 mb-2")
                self.step_info_label = ui.label("Step 0 of 0").classes("text-sm text-gray-500 text-center")

            # Time display
            self.time_label = ui.label("00:00").classes("text-2xl font-mono text-center text-gray-800 mb-6")

            # Control buttons
            with ui.row().classes("justify-center gap-4"):
                self.play_button = ui.button("▶ Start", on_click=self._toggle_play).classes(
                    "px-8 py-3 text-lg bg-blue-500 hover:bg-blue-600 text-white rounded-full shadow-md hover:shadow-lg transition-all"
                )
                ui.button("⏮ Previous", on_click=self._previous_step).classes(
                    "px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-full shadow-md hover:shadow-lg transition-all"
                )
                ui.button("⏭ Next", on_click=self._next_step).classes(
                    "px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-full shadow-md hover:shadow-lg transition-all"
                )
                ui.button("🔄 Restart", on_click=self._restart).classes(
                    "px-6 py-3 bg-indigo-500 hover:bg-indigo-600 text-white rounded-full shadow-md hover:shadow-lg transition-all"
                )

        # Initialize display
        self._update_display()

    def _toggle_play(self):
        """Toggle play/pause state"""
        if not self.session or not self.session.instructions:
            return

        if not self.is_playing:
            self._start_meditation()
        else:
            self._pause_meditation()

    def _start_meditation(self):
        """Start or resume the meditation"""
        if not self.session or not self.session.instructions:
            return

        self.is_playing = True
        self.is_paused = False

        if self.play_button:
            self.play_button.set_text("⏸ Pause")

        # Start the current step if we're at the beginning or resuming
        if self.current_step < len(self.session.instructions):
            self._start_current_step()

    def _pause_meditation(self):
        """Pause the meditation"""
        self.is_playing = False
        self.is_paused = True

        if self.play_button:
            self.play_button.set_text("▶ Resume")

        # Stop the timer
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def _restart(self):
        """Restart the meditation from the beginning"""
        if self.timer:
            self.timer.cancel()
            self.timer = None

        self.current_step = 0
        self.is_playing = False
        self.is_paused = False

        if self.play_button:
            self.play_button.set_text("▶ Start")

        self._update_display()

    def _previous_step(self):
        """Go to the previous instruction"""
        if self.current_step > 0:
            if self.timer:
                self.timer.cancel()
                self.timer = None

            self.current_step -= 1
            self._update_display()

            # If we were playing, start the new step
            if self.is_playing:
                self._start_current_step()

    def _next_step(self):
        """Go to the next instruction"""
        if not self.session or not self.session.instructions:
            return

        if self.current_step < len(self.session.instructions) - 1:
            if self.timer:
                self.timer.cancel()
                self.timer = None

            self.current_step += 1
            self._update_display()

            # If we were playing, start the new step
            if self.is_playing:
                self._start_current_step()

    def _start_current_step(self):
        """Start the current instruction step"""
        if not self.session or not self.session.instructions:
            return

        if self.current_step >= len(self.session.instructions):
            self._meditation_complete()
            return

        instruction = self.session.instructions[self.current_step]
        self._update_display()

        # If this instruction has a duration, set up a timer
        if instruction.duration_seconds and instruction.duration_seconds > 0:
            self.timer = ui.timer(instruction.duration_seconds, self._advance_to_next_step, once=True)

    def _advance_to_next_step(self):
        """Automatically advance to the next step"""
        if not self.is_playing:
            return

        self.current_step += 1

        if not self.session or self.current_step >= len(self.session.instructions):
            self._meditation_complete()
        else:
            self._start_current_step()

    def _meditation_complete(self):
        """Handle meditation completion"""
        self.is_playing = False

        if self.play_button:
            self.play_button.set_text("✓ Complete")

        if self.instruction_label:
            self.instruction_label.set_text("🙏 Meditation complete. Take a moment to notice how you feel.")

        ui.notify("Meditation session complete! 🧘‍♀️", type="positive")

        if self.timer:
            self.timer.cancel()
            self.timer = None

    def _update_display(self):
        """Update the UI display with current step information"""
        if not self.session or not self.session.instructions:
            return

        total_steps = len(self.session.instructions)

        # Update progress
        if self.progress_bar:
            progress_value = (self.current_step / max(total_steps - 1, 1)) if total_steps > 0 else 0
            self.progress_bar.set_value(progress_value)

        # Update step info
        if self.step_info_label:
            self.step_info_label.set_text(f"Step {self.current_step + 1} of {total_steps}")

        # Update instruction text
        if self.instruction_label and self.current_step < total_steps:
            instruction = self.session.instructions[self.current_step]
            self.instruction_label.set_text(instruction.instruction_text)

        # Update time display (simple step counter for now)
        if self.time_label:
            current_time = sum(inst.duration_seconds or 0 for inst in self.session.instructions[: self.current_step])
            minutes = current_time // 60
            seconds = current_time % 60
            self.time_label.set_text(f"{minutes:02d}:{seconds:02d}")


def create():
    """Create the meditation player routes"""

    @ui.page("/meditation/{session_id}")
    def meditation_page(session_id: int):
        # Apply calming theme
        ui.colors(
            primary="#3b82f6",  # Blue
            secondary="#64748b",  # Gray
            accent="#10b981",  # Green
            positive="#10b981",
            negative="#ef4444",
            warning="#f59e0b",
            info="#6366f1",  # Indigo
        )

        # Page styling
        ui.add_head_html("""
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
        </style>
        """)

        with ui.column().classes("w-full min-h-screen p-4"):
            # Back navigation
            with ui.row().classes("w-full max-w-4xl mx-auto mb-4"):
                ui.button("← Back to Sessions", on_click=lambda: ui.navigate.to("/")).classes(
                    "px-4 py-2 bg-white hover:bg-gray-50 text-gray-700 rounded-lg shadow-md"
                )

            # Create meditation player
            player = MeditationPlayer(session_id)
            player.create()
