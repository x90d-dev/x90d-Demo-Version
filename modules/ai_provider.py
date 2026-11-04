import os

try:
    import requests
except ImportError:  # pragma: no cover - dependency is installed in normal setup
    requests = None

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


if load_dotenv:
    load_dotenv()


DEFAULT_MODEL = "qwen2.5:3b"


def _timeout() -> int:
    try:
        return int(os.getenv("OLLAMA_TIMEOUT", "120"))
    except ValueError:
        return 120


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def generate_ai_response(prompt: str, images: list[str] | None = None, model_override: str | None = None) -> str:
    if not prompt.strip():
        return "Soal masih kosong. Tulis soal terlebih dahulu."
    if requests is None:
        return "Dependency requests belum terinstall. Jalankan: pip install -r requirements.txt"

    base_url = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
    model = model_override or os.getenv("OLLAMA_MODEL", DEFAULT_MODEL) or DEFAULT_MODEL
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": _env_float("OLLAMA_TEMPERATURE", 0.1),
            "top_p": _env_float("OLLAMA_TOP_P", 0.85),
            "repeat_penalty": _env_float("OLLAMA_REPEAT_PENALTY", 1.08),
            "num_ctx": _env_int("OLLAMA_NUM_CTX", 2048),
        },
    }
    if images:
        payload["images"] = images

    try:
        response = requests.post(f"{base_url}/api/generate", json=payload, timeout=_timeout())
    except requests.exceptions.ConnectionError:
        return "Ollama belum berjalan. Jalankan: ollama serve"
    except requests.exceptions.Timeout:
        return "Model terlalu lama merespons. Coba ulangi dengan soal yang lebih pendek."
    except requests.exceptions.RequestException:
        return "Terjadi kendala saat menghubungi Ollama. Pastikan Ollama berjalan dengan benar."

    if response.status_code == 404:
        return f"Model belum tersedia. Jalankan: ollama pull {model}"
    if response.status_code >= 400:
        return "Ollama mengembalikan error. Pastikan model sudah diunduh dan coba lagi."

    try:
        data = response.json()
    except ValueError:
        return "Respons Ollama tidak bisa dibaca. Coba ulangi beberapa saat lagi."

    answer = (data.get("response") or "").strip()
    if not answer:
        return "Respons Ollama kosong. Coba ulangi dengan soal yang lebih pendek."
    return answer
