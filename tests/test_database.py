"""SQLite repository tests."""

from core.schemas import CrossingEvent
from database.repository import TrafficRepository


def test_sqlite_session_and_event_insertion_are_consistent(tmp_path):
    repository = TrafficRepository(tmp_path / "trafficvision.db")
    session_id = repository.create_session("synthetic.mp4", session_id="session-1")
    event = CrossingEvent(1, "main_line", "car", "A_TO_B", 12, 600.0, (10.0, 50.0))

    assert repository.add_event(session_id, event) is True
    assert repository.add_event(session_id, event) is False
    repository.save_statistics(session_id, {"total_vehicles": 1, "by_class": {"car": 1}, "by_direction": {"a_to_b": 1}})
    repository.finish_session(session_id)

    assert len(repository.list_sessions()) == 1
    assert repository.get_events(session_id)[0]["class_name"] == "car"
    repository.close()


def test_sqlite_foreign_keys_are_enabled(tmp_path):
    repository = TrafficRepository(tmp_path / "trafficvision.db")

    assert repository.connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    repository.close()
