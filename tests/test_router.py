from modules.ai_router import detect_question_type, detect_subject


def test_detect_subject_math():
    assert detect_subject("Selesaikan persamaan 2x + 3 = 11") == "matematika"


def test_detect_subject_toefl():
    assert detect_subject("TOEFL Structure: The teacher ___ here.") == "toefl"


def test_detect_subject_coding():
    assert detect_subject("Buat aplikasi Python Flask dengan SQLite") == "coding"


def test_detect_subject_history_indonesia_independence():
    assert detect_subject("Kapan Indonesia merdeka?") == "sejarah"


def test_detect_question_type_multiple_choice():
    question = "Pilih jawaban benar:\nA. satu\nB. dua\nC. tiga\nD. empat"
    assert detect_question_type(question) == "multiple_choice"


def test_detect_question_type_reading():
    assert detect_question_type("Reading comprehension: read the text and answer.") == "reading"
