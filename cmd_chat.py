import os
import sys

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is installed in normal setup
    load_dotenv = None

from modules.agent_manager import AGENT_PROFILES
from modules.chat_manager import (
    DEFAULT_REASONING_LEVEL,
    MODE_LABELS,
    chat_with_ai,
    trim_chat_history,
)


MODE_ALIASES = {
    "auto": "auto",
    "otomatis": "auto",
    "general": "general",
    "umum": "general",
    "chat": "general",
    "thinking": "thinking",
    "think": "thinking",
    "tutor": "tutor",
    "task": "task",
    "tugas": "task",
    "english": "english_toefl",
    "toefl": "english_toefl",
    "english_toefl": "english_toefl",
    "coding": "coding",
    "kode": "coding",
    "developer": "coding",
    "dev": "coding",
}

AGENT_ALIASES = {
    "normal": "normal",
    "biasa": "normal",
    "agent": "agent",
    "agen": "agent",
}


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def format_banner() -> str:
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    return (
        "CoreChiperAgent CMD Chat\n"
        f"Model: {model}\n"
        "Pastikan Ollama sudah berjalan sebelum mulai chat.\n"
        "Perintah: /help, /mode coding, /agent agent, /clear, /exit"
    )


def format_help() -> str:
    modes = ", ".join(MODE_LABELS.keys())
    agents = ", ".join(AGENT_PROFILES.keys())
    return (
        "Bantuan CMD Chat:\n"
        "- Tulis pesan biasa lalu tekan Enter untuk chat.\n"
        f"- /mode <mode> untuk mengganti mode. Pilihan: {modes}\n"
        f"- /agent <cara kerja> untuk mengganti cara kerja. Pilihan: {agents}\n"
        "- /clear untuk menghapus riwayat sesi CMD sementara.\n"
        "- /exit untuk keluar."
    )


def parse_command(raw_text: str, current_mode: str = "auto", current_agent: str = "normal") -> dict:
    text = (raw_text or "").strip()
    if not text:
        return {"type": "empty"}
    if not text.startswith("/"):
        return {"type": "message", "message": text}

    parts = text.split(maxsplit=1)
    command = parts[0].lower()
    argument = parts[1].strip().lower() if len(parts) > 1 else ""

    if command in {"/exit", "/quit", "/q"}:
        return {"type": "exit"}
    if command == "/help":
        return {"type": "help"}
    if command == "/clear":
        return {"type": "clear"}
    if command == "/status":
        return {"type": "status", "mode": current_mode, "agent_profile": current_agent}

    if command == "/mode":
        resolved_mode = MODE_ALIASES.get(argument)
        if resolved_mode:
            return {"type": "mode", "mode": resolved_mode}
        choices = ", ".join(sorted(MODE_ALIASES.keys()))
        return {"type": "error", "message": f"Mode tidak dikenal. Pilihan: {choices}"}

    if command == "/agent":
        resolved_agent = AGENT_ALIASES.get(argument)
        if resolved_agent:
            return {"type": "agent", "agent_profile": resolved_agent}
        choices = ", ".join(sorted(AGENT_ALIASES.keys()))
        return {"type": "error", "message": f"Cara kerja tidak dikenal. Pilihan: {choices}"}

    return {"type": "error", "message": "Perintah tidak dikenal. Ketik /help untuk melihat bantuan."}


def run_chat_loop() -> int:
    mode = "auto"
    agent_profile = "normal"
    history = []

    print(format_banner())
    while True:
        try:
            raw_message = input("\nAdmin> ")
        except (EOFError, KeyboardInterrupt):
            print("\nKeluar dari CMD Chat.")
            return 0

        parsed = parse_command(raw_message, current_mode=mode, current_agent=agent_profile)
        command_type = parsed["type"]

        if command_type == "empty":
            continue
        if command_type == "exit":
            print("Sampai jumpa, Admin.")
            return 0
        if command_type == "help":
            print(format_help())
            continue
        if command_type == "clear":
            history = []
            print("Riwayat sesi CMD dibersihkan.")
            continue
        if command_type == "status":
            print(
                f"Mode: {MODE_LABELS.get(mode, mode)} | "
                f"Cara kerja: {AGENT_PROFILES.get(agent_profile, agent_profile)}"
            )
            continue
        if command_type == "mode":
            mode = parsed["mode"]
            print(f"Mode diubah ke {MODE_LABELS.get(mode, mode)}.")
            continue
        if command_type == "agent":
            agent_profile = parsed["agent_profile"]
            print(f"Cara kerja diubah ke {AGENT_PROFILES.get(agent_profile, agent_profile)}.")
            continue
        if command_type == "error":
            print(parsed["message"])
            continue

        user_message = parsed["message"]
        print("\nCoreChiperAgent sedang berpikir...\n")
        try:
            result = chat_with_ai(
                user_message,
                mode,
                history=history,
                reasoning_level=DEFAULT_REASONING_LEVEL,
                agent_profile=agent_profile,
            )
            response = result.get("response", "").strip()
        except Exception as exc:
            response = f"Terjadi masalah saat memproses pesan: {exc}"

        print("CoreChiperAgent:")
        print(response or "Respons kosong. Coba ulangi dengan pesan yang lebih singkat.")
        history.append({"user_message": user_message, "ai_response": response})
        history = trim_chat_history(history, max_turns=6)


def main() -> int:
    configure_console()
    if load_dotenv:
        load_dotenv()
    return run_chat_loop()


if __name__ == "__main__":
    raise SystemExit(main())
