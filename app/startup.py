from app.database import create_tables
import app.meditation_library
import app.meditation_player


def startup() -> None:
    # this function is called before the first request
    create_tables()

    # Register meditation modules
    app.meditation_library.create()
    app.meditation_player.create()
