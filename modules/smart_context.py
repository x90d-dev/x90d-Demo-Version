import re

from modules.database import get_relevant_learning_notes


def build_smart_context(message: str, subject: str | None = None) -> str:
    text = (message or "").lower()
    hints = []

    if _has_any(text, ["top ", "ranking", "terbaru", "universitas", "harga", "berita", "tahun ini"]):
        hints.append(
            "Batasan data terbaru: tanpa web search, data ranking/top/berita/harga terbaru perlu dicek dari sumber terbaru."
        )

    if _has_any(text, ["machine learning", "ml", "feature", "fitur", "label", "target", "dataset", "prediksi", "model ai"]):
        hints.append(
            "Konsep AI/ML stabil: jangan menolak menjawab hanya karena web search gagal. Jawab langsung dari konsep dasar, lalu beri contoh konkret."
        )
        hints.append(
            "Machine learning: feature adalah variabel/input/atribut yang dipakai model untuk membuat prediksi. Label/target adalah nilai yang ingin diprediksi."
        )
        hints.append(
            "Contoh prediksi harga rumah: feature bisa berupa luas tanah, luas bangunan, jumlah kamar, jumlah kamar mandi, lokasi, usia bangunan, kondisi rumah, akses transportasi, dan jarak ke pusat kota. Target/labelnya adalah harga rumah."
        )
        hints.append(
            "Evaluasi ML: accuracy tinggi belum tentu bagus jika data imbalance, data leakage, atau metric tidak sesuai. Bandingkan precision, recall, F1, confusion matrix, dan baseline."
        )

    if _has_any(text, ["sql injection", "injection", "password hardcoded", "keamanan", "security", "xss", "csrf"]):
        hints.append(
            "Keamanan dasar: jangan menyarankan string concatenation untuk query SQL. Gunakan parameterized query/prepared statement, validasi input, secret di environment, dan prinsip least privilege."
        )

    if _has_any(text, ["typeerror", "valueerror", "traceback", "exception", "bug", "debug", "tidak jalan", "gagal jalan"]):
        hints.append(
            "Debugging: baca error message, bedakan gejala dan akar masalah, cek baris terkait, buat perbaikan minimal, lalu verifikasi dengan test atau langkah reproduksi."
        )

    if _has_any(text, ["correlation", "causation", "korelasi", "kausal", "analisis data", "bottleneck"]):
        hints.append(
            "Analisis data/teknis: bedakan korelasi dan sebab-akibat, cek kualitas data, baseline, outlier, sampling, dan metode verifikasi sebelum menyimpulkan."
        )

    if _has_any(text, ["pasti", "selalu", "tidak pernah", "hanya", "semua"]):
        hints.append(
            "Pertanyaan jebakan: waspadai kata ekstrem seperti pasti/selalu/hanya/tidak pernah. Koreksi premis jika keliru dan jangan menjawab terlalu percaya diri."
        )

    if _has_any(text, ["gaya", "newton", "massa", "percepatan", "kecepatan", "detik"]):
        hints.append(
            "Fisika: Hukum II Newton adalah F = m x a, jadi a = F / m. Hasil F/m adalah percepatan, bukan kecepatan. Jika ditanya kecepatan setelah t detik dan benda mula-mula diam, gunakan v = a x t."
        )
        hints.append(
            "Cek satuan fisika: gaya N, massa kg, percepatan m/s^2, kecepatan m/s, waktu s."
        )

    if _has_any(text, ["persamaan", "linear", "2x", "3x", "nilai x", "aljabar"]):
        hints.append(
            "Matematika: untuk persamaan linear satu variabel, pindahkan konstanta dengan operasi kebalikan, lalu bagi dengan koefisien variabel. Cek hasil dengan substitusi ke persamaan awal."
        )

    if _has_any(text, ["rasio", "perbandingan", "mula-mula", "setelah", "total akhir", "jumlah akhir", "transfer"]):
        hints.append(
            "Matematika deep_check_mode: untuk rasio/perubahan, buat kondisi awal, terapkan perubahan ke pihak yang benar, bentuk kondisi akhir, lalu validasi rasio akhir dan total akhir. Jika syarat bertentangan, jawab tidak ada solusi."
        )

    if _has_any(text, ["mol", "mr", "massa molar", "stoikiometri"]):
        hints.append("Kimia: jumlah mol n = massa / Mr. Pastikan massa dalam gram dan Mr dalam g/mol.")

    if _has_any(text, ["ph", "asam", "basa"]):
        hints.append("Kimia: pH < 7 asam, pH = 7 netral, pH > 7 basa.")

    if _has_any(text, ["grammar", "verb", "subject", "toefl", "structure"]):
        hints.append(
            "Bahasa Inggris/TOEFL: cari subject utama sebelum memilih verb. Frasa sisipan seperti along with tidak mengubah jumlah subject utama."
        )

    if subject == "coding" or _has_any(text, ["python", "kode", "coding", "aplikasi", "debug", "flask", "sqlite", "api"]):
        hints.append(
            "Coding/Developer: ikuti memori training coding jika ada. Untuk aplikasi, berikan struktur folder, kode per file, cara menjalankan, cara test, dan hindari kode toy."
        )

    notes = get_relevant_learning_notes(message, subject=subject, limit=8)
    for note in notes:
        hints.append(f"Memori koreksi ({note['subject']}): jika ada '{note['trigger_text']}', ikuti koreksi: {note['correction']}")

    if not hints:
        return ""

    compact = "\n".join(f"- {hint}" for hint in hints[:10])
    return f"Konteks pemeriksaan yang harus dipakai bila relevan:\n{compact}"


def _has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)
