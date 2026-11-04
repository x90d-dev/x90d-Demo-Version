import os
from collections import Counter
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for

from modules.agent_manager import AGENT_PROFILES, resolve_agent_profile
from modules.ai_router import detect_question_type
from modules.ai_solver import solve_question
from modules.answer_checker import check_answer
from modules.attachment_handler import prepare_chat_attachment
from modules.chat_manager import DEFAULT_REASONING_LEVEL, MODE_LABELS, REASONING_LEVELS, chat_with_ai, should_use_chat_history
from modules.database import (
    clear_chat_history,
    create_user,
    create_chat_thread,
    delete_chat_thread,
    get_chat_thread,
    get_chat_threads,
    get_user_by_id,
    get_learning_notes,
    get_practice_history,
    get_recent_chat_history,
    get_progress_rows,
    init_db,
    insert_question,
    save_chat_message,
    save_learning_note,
    verify_user,
)
from modules.progress_tracker import get_progress_summary, save_practice_result, update_progress
from modules.pdf_processor import PDFProcessingError, build_pdf_context
from modules.pdf_session import clear_current_pdf, get_current_pdf, set_current_pdf
from modules.rag_engine import load_question_bank
from modules.training_seed import BRUTAL_TRAINING_NOTES, install_brutal_training_pack
from modules.web_search import format_web_context, search_web, should_auto_web_search


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "local-dev-secret")

DEFAULT_VISION_MODEL = "moondream"
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_DEFAULT_PASSWORD", "dhafir012")

SUBJECT_OPTIONS = [
    ("auto", "Deteksi otomatis"),
    ("matematika", "Matematika"),
    ("fisika", "Fisika"),
    ("kimia", "Kimia"),
    ("bahasa_inggris", "Bahasa Inggris"),
    ("sejarah", "Sejarah"),
    ("pendidikan", "Pendidikan"),
    ("toefl", "TOEFL"),
    ("coding", "Coding / Developer"),
]

CHAT_MODE_OPTIONS = [
    ("auto", "Otomatis"),
    ("thinking", "Thinking Mode"),
    ("general", "Chat Umum"),
    ("tutor", "Tutor"),
    ("task", "Tugas"),
    ("english_toefl", "TOEFL/English"),
    ("coding", "Developer Mode"),
]

AGENT_PROFILE_OPTIONS = [
    ("normal", "Normal"),
    ("agent", "Agent"),
]

TRAINING_SUBJECT_OPTIONS = SUBJECT_OPTIONS[1:] + [("umum", "Umum")]

REASONING_LEVEL_OPTIONS = [
    ("basic", "Basic"),
    ("menjebak", "Menjebak"),
    ("level_tinggi", "Level Tinggi"),
    ("super_sulit", "Super Sulit"),
]


def get_vision_model() -> str:
    selected = (os.getenv("OLLAMA_VISION_MODEL") or DEFAULT_VISION_MODEL).strip()
    if selected.lower() in {"none", "off", "false", "0", "disable", "disabled"}:
        return ""
    return selected or DEFAULT_VISION_MODEL


def is_admin_logged_in() -> bool:
    return session.get("user_role") == "admin"


def get_display_name() -> str:
    user = g.get("current_user")
    if not user:
        return "Admin"
    if user["role"] == "admin":
        return "Admin"
    return user["username"] or "User"


def get_display_initial() -> str:
    name = get_display_name().strip()
    return (name[:1] or "U").upper()


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not is_admin_logged_in():
            flash("Menu Training hanya bisa dibuka setelah login.", "warning")
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)

    return wrapper


def get_current_thread_id() -> int | None:
    thread_id = session.get("current_thread_id")
    if not thread_id:
        return None
    if not get_chat_thread(thread_id):
        session.pop("current_thread_id", None)
        return None
    return int(thread_id)


def ensure_current_thread(user_message: str = "Chat baru") -> int:
    thread_id = get_current_thread_id()
    if thread_id:
        return thread_id
    thread_id = create_chat_thread(user_message or "Chat baru")
    session["current_thread_id"] = thread_id
    return thread_id


def get_chat_prompt_history(selected_mode: str, message: str, thread_id: int | None = None) -> list:
    selected = (selected_mode or "auto").strip().lower()
    history_mode = None if selected == "auto" else selected
    if selected == "auto" and not should_use_chat_history(message):
        return []
    return get_recent_chat_history(mode=history_mode, limit=6, thread_id=thread_id)


def process_chat_submission(form, files, selected_mode: str, selected_reasoning_level: str, selected_agent_profile: str) -> dict:
    user_message = form.get("message", "").strip()
    web_search_requested = form.get("web_search") == "on"
    uploaded_file = files.get("attachment")
    agent_profile = resolve_agent_profile(selected_agent_profile)
    vision_model = get_vision_model()
    attachment = prepare_chat_attachment(uploaded_file, vision_enabled=bool(vision_model))

    if attachment["pdf_document"] and not user_message:
        user_message = "Ringkas PDF ini."

    if not user_message and not attachment["prompt_context"] and not attachment["pdf_document"]:
        raise ValueError("Pesan chat tidak boleh kosong.")

    ai_message = f"{user_message}{attachment['prompt_context']}".strip()
    display_message = user_message or "Tolong analisis file ini."
    if attachment["display_note"]:
        display_message = f"{display_message}\n\n{attachment['display_note']}"

    extra_parts = []
    web_search_status = ""
    active_pdf = attachment["pdf_document"] or get_current_pdf()
    if attachment["pdf_document"]:
        set_current_pdf(attachment["pdf_document"])
        active_pdf = attachment["pdf_document"]
    if active_pdf:
        extra_parts.append(build_pdf_context(user_message, active_pdf))

    should_search = web_search_requested or should_auto_web_search(user_message)
    if should_search and user_message:
        max_results = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5") or 5)
        web_result = search_web(user_message, max_results=max_results)
        extra_parts.append(format_web_context(web_result))
        if web_result.get("ok"):
            web_search_status = f"Web search aktif: {len(web_result.get('results', []))} sumber ditemukan."
            display_message = f"{display_message}\n\n[Web search aktif]"
        else:
            web_search_status = web_result.get("error", "Web search gagal.")
            display_message = f"{display_message}\n\n[Web search gagal: {web_search_status}]"

    thread_id = ensure_current_thread(user_message)
    prompt_history = get_chat_prompt_history(selected_mode, user_message, thread_id=thread_id)
    chat_result = chat_with_ai(
        ai_message,
        selected_mode,
        prompt_history,
        images=attachment["images"],
        model_override=vision_model if attachment["images"] else None,
        extra_context="\n\n".join(part for part in extra_parts if part),
        reasoning_level=selected_reasoning_level,
        agent_profile=agent_profile,
    )
    save_chat_message(chat_result["mode"], display_message, chat_result["response"], thread_id=thread_id)
    return {
        "chat_result": chat_result,
        "display_message": display_message,
        "user_message": user_message,
        "web_search_status": web_search_status,
        "selected_mode": selected_mode,
        "selected_agent_profile": agent_profile,
        "thread_id": thread_id,
    }


@app.before_request
def ensure_database():
    init_db()
    user_id = session.get("user_id")
    g.current_user = get_user_by_id(user_id) if user_id else None


@app.context_processor
def inject_auth_context():
    return {
        "current_user": g.get("current_user"),
        "is_admin": is_admin_logged_in(),
        "display_name": get_display_name(),
        "display_initial": get_display_initial(),
    }


@app.route("/")
def index():
    return redirect(url_for("chat"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_id = request.form.get("login", "").strip()
        password = request.form.get("password", "")
        user = verify_user(login_id, password)
        if not user:
            flash("Login gagal. Periksa username/email dan password.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["user_role"] = user["role"]
        flash(f"Selamat datang, {user['username']}.", "success")
        next_url = request.args.get("next") or url_for("chat")
        return redirect(next_url)

    return render_template("login.html", default_admin_password=DEFAULT_ADMIN_PASSWORD)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            create_user(username, email, password, role="user")
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("register"))
        except Exception:
            flash("Username atau email sudah dipakai.", "error")
            return redirect(url_for("register"))
        flash("Akun berhasil dibuat. Silakan login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Logout berhasil.", "success")
    return redirect(url_for("chat"))


@app.route("/login/<provider>")
def social_login(provider: str):
    provider_name = (provider or "provider").title()
    flash(f"Login {provider_name} belum dikonfigurasi untuk lokal. Gunakan login email/password.", "warning")
    return redirect(url_for("login"))


@app.route("/home")
def home():
    return render_template("index.html", subject_options=SUBJECT_OPTIONS)


@app.route("/solve", methods=["POST"])
def solve():
    question = request.form.get("question", "").strip()
    selected_subject = request.form.get("subject", "auto")

    if not question:
        flash("Soal tidak boleh kosong.", "error")
        return redirect(url_for("home"))

    try:
        result = solve_question(question, selected_subject)
        insert_question(
            subject=result["subject"],
            topic=result["topic"],
            question_text=question,
            answer=result["answer"],
            explanation=result.get("context_used", ""),
            level=1,
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("home"))
    except Exception:
        flash("Terjadi error saat memproses soal. Coba ulangi dengan soal yang lebih pendek.", "error")
        return redirect(url_for("home"))

    return render_template("result.html", question=question, result=result)


@app.route("/chat", methods=["GET", "POST"])
def chat():
    selected_mode = request.form.get("mode", request.args.get("mode", "auto"))
    selected_reasoning_level = request.form.get("reasoning_level", request.args.get("reasoning_level", DEFAULT_REASONING_LEVEL))
    selected_agent_profile = resolve_agent_profile(request.form.get("agent_profile", request.args.get("agent_profile", "normal")))
    chat_result = None
    user_message = ""
    web_search_status = ""

    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        web_search_requested = request.form.get("web_search") == "on"
        uploaded_file = request.files.get("attachment")
        vision_model = get_vision_model()
        try:
            attachment = prepare_chat_attachment(uploaded_file, vision_enabled=bool(vision_model))
        except PDFProcessingError as exc:
            flash(str(exc), "error")
            return redirect(url_for("chat"))
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("chat"))

        if attachment["pdf_document"] and not user_message:
            user_message = "Ringkas PDF ini."

        if not user_message and not attachment["prompt_context"] and not attachment["pdf_document"]:
            flash("Pesan chat tidak boleh kosong.", "error")
            return redirect(url_for("chat"))

        try:
            ai_message = f"{user_message}{attachment['prompt_context']}".strip()
            display_message = user_message or "Tolong analisis file ini."
            if attachment["display_note"]:
                display_message = f"{display_message}\n\n{attachment['display_note']}"

            extra_context = ""
            active_pdf = attachment["pdf_document"] or get_current_pdf()
            if attachment["pdf_document"]:
                set_current_pdf(attachment["pdf_document"])
                active_pdf = attachment["pdf_document"]
            if active_pdf:
                pdf_context = build_pdf_context(user_message, active_pdf)
                extra_context = "\n\n".join(part for part in [extra_context, pdf_context] if part)

            should_search = web_search_requested or should_auto_web_search(user_message)
            if should_search and user_message:
                max_results = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5") or 5)
                web_result = search_web(user_message, max_results=max_results)
                extra_context = "\n\n".join(part for part in [extra_context, format_web_context(web_result)] if part)
                if web_result.get("ok"):
                    web_search_status = f"Web search aktif: {len(web_result.get('results', []))} sumber ditemukan."
                    display_message = f"{display_message}\n\n[Web search aktif]"
                else:
                    web_search_status = web_result.get("error", "Web search gagal.")
                    display_message = f"{display_message}\n\n[Web search gagal: {web_search_status}]"

            requested_mode = selected_mode
            thread_id = ensure_current_thread(user_message)
            prompt_history = get_chat_prompt_history(requested_mode, user_message, thread_id=thread_id)
            chat_result = chat_with_ai(
                ai_message,
                requested_mode,
                prompt_history,
                images=attachment["images"],
                model_override=vision_model if attachment["images"] else None,
                extra_context=extra_context,
                reasoning_level=selected_reasoning_level,
                agent_profile=selected_agent_profile,
            )
            save_chat_message(chat_result["mode"], display_message, chat_result["response"], thread_id=thread_id)
            selected_mode = requested_mode if requested_mode == "auto" else chat_result["mode"]
            selected_reasoning_level = chat_result["reasoning_level"]
            selected_agent_profile = chat_result["agent_profile"]
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("chat"))
        except Exception:
            flash("Terjadi masalah saat memproses jawaban. Coba kirim ulang soal atau jawaban.", "error")
            return redirect(url_for("chat"))

    current_thread_id = get_current_thread_id()
    messages = get_recent_chat_history(limit=20, thread_id=current_thread_id) if current_thread_id else []
    chat_threads = get_chat_threads(limit=30)
    return render_template(
        "chat.html",
        mode_options=CHAT_MODE_OPTIONS,
        agent_profile_options=AGENT_PROFILE_OPTIONS,
        agent_profile_labels=AGENT_PROFILES,
        mode_labels=MODE_LABELS,
        selected_mode=selected_mode,
        selected_agent_profile=selected_agent_profile,
        reasoning_level_options=REASONING_LEVEL_OPTIONS,
        selected_reasoning_level=selected_reasoning_level if selected_reasoning_level in REASONING_LEVELS else DEFAULT_REASONING_LEVEL,
        reasoning_level_label=REASONING_LEVELS.get(selected_reasoning_level, REASONING_LEVELS[DEFAULT_REASONING_LEVEL]),
        messages=messages,
        chat_threads=chat_threads,
        current_thread_id=current_thread_id,
        chat_result=chat_result,
        user_message=user_message,
        web_search_status=web_search_status,
        current_pdf=get_current_pdf(),
    )


@app.route("/chat/clear", methods=["POST"])
def chat_clear():
    session.pop("current_thread_id", None)
    clear_current_pdf()
    return redirect(url_for("chat"))


@app.route("/chat/thread/<int:thread_id>")
def chat_thread(thread_id: int):
    if get_chat_thread(thread_id):
        session["current_thread_id"] = thread_id
    return redirect(url_for("chat"))


@app.route("/chat/thread/<int:thread_id>/delete", methods=["POST"])
def chat_thread_delete(thread_id: int):
    delete_chat_thread(thread_id)
    if session.get("current_thread_id") == thread_id:
        session.pop("current_thread_id", None)
        clear_current_pdf()
    return redirect(url_for("chat"))


@app.route("/chat/send", methods=["POST"])
def chat_send():
    selected_mode = request.form.get("mode", "auto")
    selected_reasoning_level = request.form.get("reasoning_level", DEFAULT_REASONING_LEVEL)
    selected_agent_profile = request.form.get("agent_profile", "normal")
    try:
        result = process_chat_submission(request.form, request.files, selected_mode, selected_reasoning_level, selected_agent_profile)
    except (PDFProcessingError, ValueError) as exc:
        return jsonify({"ok": False, "message": str(exc)}), 400
    except Exception:
        return jsonify({
            "ok": False,
            "message": "Terjadi masalah saat memproses jawaban. Coba kirim ulang soal atau jawaban.",
        }), 500

    chat_result = result["chat_result"]
    return jsonify({
        "ok": True,
        "user_message": result["display_message"],
        "ai_response": chat_result["response"],
        "mode": chat_result["mode"],
        "mode_label": chat_result["mode_label"],
        "selected_mode": result["selected_mode"],
        "reasoning_level": chat_result["reasoning_level"],
        "reasoning_level_label": chat_result["reasoning_level_label"],
        "agent_profile": chat_result["agent_profile"],
        "agent_profile_label": chat_result["agent_profile_label"],
        "selected_agent_profile": result["selected_agent_profile"],
        "thread_id": result["thread_id"],
        "web_search_status": result["web_search_status"],
    })


@app.route("/practice")
def practice():
    subject_filter = request.args.get("subject", "all")
    questions = load_question_bank()
    if subject_filter != "all":
        questions = [item for item in questions if item.get("subject") == subject_filter]
    return render_template(
        "practice.html",
        questions=questions,
        subject_options=SUBJECT_OPTIONS[1:],
        subject_filter=subject_filter,
    )


@app.route("/practice/check", methods=["POST"])
def practice_check():
    question = request.form.get("question", "").strip()
    user_answer = request.form.get("user_answer", "").strip()
    correct_answer = request.form.get("correct_answer", "").strip()
    subject = request.form.get("subject", "umum").strip()
    topic = request.form.get("topic", "umum").strip()
    level = int(request.form.get("level", "1") or 1)
    question_type = request.form.get("question_type") or detect_question_type(question)

    result = check_answer(user_answer, correct_answer, subject, question_type)
    save_practice_result(
        subject=subject,
        topic=topic,
        question=question,
        user_answer=user_answer,
        correct_answer=correct_answer,
        is_correct=result["is_correct"],
        mistake_note=result["mistake_note"],
        level=level,
    )
    progress = update_progress(
        subject=subject,
        topic=topic,
        is_correct=result["is_correct"],
        mistake_note=result["mistake_note"],
        level=level,
    )

    flash(result["feedback"], "success" if result["is_correct"] else "warning")
    return render_template(
        "practice.html",
        questions=load_question_bank(),
        subject_options=SUBJECT_OPTIONS[1:],
        subject_filter="all",
        checked_result=result,
        checked_question=question,
        checked_answer=user_answer,
        correct_answer=correct_answer,
        progress=progress,
    )


@app.route("/history")
def history():
    return render_template(
        "history.html",
        history=get_practice_history(),
        progress_rows=get_progress_summary(),
    )


@app.route("/training")
@admin_required
def training():
    questions = load_question_bank()
    subject_counts = Counter(item.get("subject", "umum") for item in questions)
    return render_template(
        "training.html",
        subject_counts=subject_counts,
        total_questions=len(questions),
        progress_rows=get_progress_rows(),
        learning_notes=get_learning_notes(limit=10),
        subject_options=TRAINING_SUBJECT_OPTIONS,
        brutal_training_count=len(BRUTAL_TRAINING_NOTES),
    )


@app.route("/training/note", methods=["POST"])
@admin_required
def training_note():
    subject = request.form.get("subject", "umum").strip()
    trigger_text = request.form.get("trigger_text", "").strip()
    correction = request.form.get("correction", "").strip()

    if not trigger_text or not correction:
        flash("Trigger dan koreksi harus diisi.", "error")
        return redirect(url_for("training"))
    if len(trigger_text) > 300 or len(correction) > 1000:
        flash("Catatan terlalu panjang. Ringkas agar model lokal tetap ringan.", "error")
        return redirect(url_for("training"))

    save_learning_note(subject, trigger_text, correction)
    flash("Memori koreksi lokal sudah disimpan.", "success")
    return redirect(url_for("training"))


@app.route("/training/seed/brutal", methods=["POST"])
@admin_required
def training_seed_brutal():
    result = install_brutal_training_pack()
    flash(
        f"Paket Training Brutal terpasang. Baru: {result['inserted']}, sudah ada: {result['skipped']}.",
        "success",
    )
    return redirect(url_for("training"))


@app.route("/report")
def report():
    progress_rows = get_progress_summary()
    history_rows = get_practice_history(limit=10)
    chat_rows = get_recent_chat_history(limit=10)
    return render_template(
        "report.html",
        progress_rows=progress_rows,
        history=history_rows,
        chat_rows=chat_rows,
    )


@app.errorhandler(404)
def not_found(_error):
    return render_template("result.html", question="", result={
        "subject": "umum",
        "topic": "halaman tidak ditemukan",
        "question_type": "essay",
        "answer": "Halaman tidak ditemukan. Gunakan menu Home, Chat, Latihan, Riwayat, Training, atau Report.",
        "context_used": "",
    }), 404


if __name__ == "__main__":
    init_db()
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=os.getenv("FLASK_ENV", "development") == "development",
        use_reloader=False,
    )
