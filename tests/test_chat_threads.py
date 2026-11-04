from modules.database import (
    create_chat_thread,
    delete_chat_thread,
    get_chat_threads,
    get_recent_chat_history,
    init_db,
    save_chat_message,
)


def test_chat_thread_can_store_and_reload_messages(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "threads.db"))
    init_db()

    thread_id = create_chat_thread("Bahas Python")
    save_chat_message("coding", "buat script python", "jawaban", thread_id=thread_id)

    messages = get_recent_chat_history(thread_id=thread_id, limit=10)
    threads = get_chat_threads()

    assert len(messages) == 1
    assert messages[0]["user_message"] == "buat script python"
    assert any(thread["id"] == thread_id for thread in threads)


def test_delete_chat_thread_removes_only_selected_thread(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "threads.db"))
    init_db()

    keep_thread = create_chat_thread("Tetap")
    remove_thread = create_chat_thread("Hapus")
    save_chat_message("general", "pesan tetap", "ok", thread_id=keep_thread)
    save_chat_message("general", "pesan hapus", "ok", thread_id=remove_thread)

    delete_chat_thread(remove_thread)

    assert get_recent_chat_history(thread_id=keep_thread, limit=10)
    assert get_recent_chat_history(thread_id=remove_thread, limit=10) == []
    assert all(thread["id"] != remove_thread for thread in get_chat_threads())
