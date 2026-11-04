from modules.agent_manager import build_agent_context, resolve_agent_profile, should_use_agent_flow


def test_resolve_agent_profile_defaults_to_normal():
    assert resolve_agent_profile("unknown") == "normal"
    assert resolve_agent_profile("agent") == "agent"


def test_agent_flow_detects_work_command():
    assert should_use_agent_flow("Buatkan aplikasi Python sederhana", "normal")
    assert should_use_agent_flow("Apa kabar?", "agent")


def test_agent_context_includes_personal_work_agent_rules():
    context = build_agent_context("Buatkan aplikasi Python", profile="agent", has_pdf=True, has_images=True)
    lowered = context.lower()

    assert "personal work agent" in lowered
    assert "tujuan, rencana singkat, eksekusi, validasi" in lowered
    assert "pdf aktif" in lowered
    assert "gambar aktif" in lowered


def test_normal_context_stays_lightweight():
    context = build_agent_context("jelaskan feature machine learning", profile="normal")
    lowered = context.lower()

    assert "cara kerja: normal" in lowered
    assert "jangan membuat rencana panjang" in lowered
