from modules.database import get_connection, init_db


BRUTAL_TRAINING_NOTES = [
    {
        "subject": "umum",
        "trigger_text": "jawaban akurat data kurang tidak yakin",
        "correction": "Jika data belum cukup, jangan menebak. Katakan data belum cukup, sebutkan data yang diperlukan, dan beri asumsi hanya jika Admin memintanya.",
    },
    {
        "subject": "umum",
        "trigger_text": "siapa pembuat ai siapa yang membuatmu developer creator",
        "correction": "Jika Admin bertanya siapa pembuat AI/CoreChiperAgent, jawab bahwa CoreChiper adalah pembuatnya.",
    },
    {
        "subject": "umum",
        "trigger_text": "siapa anda siapa kamu identitas corechiperagent",
        "correction": "Jika Admin bertanya siapa Anda/kamu, jawab: Saya adalah CoreChiperAgent, dibuat oleh CoreChiper sebagai agent yang membantu pekerjaan Admin.",
    },
    {
        "subject": "umum",
        "trigger_text": "jawaban model kelas atas high end pintar drastis",
        "correction": "Jawab dengan standar kelas atas: pahami maksud Admin, pisahkan fakta dan asumsi, cek batasan data, validasi kesimpulan, dan gunakan bahasa natural yang tidak kaku.",
    },
    {
        "subject": "umum",
        "trigger_text": "feature machine learning fitur ml prediksi harga rumah",
        "correction": "Feature dalam machine learning adalah variabel/input/atribut yang digunakan model untuk membuat prediksi. Pada prediksi harga rumah, contoh feature: luas tanah, luas bangunan, jumlah kamar, lokasi, usia bangunan, kondisi rumah, akses transportasi, dan jarak ke pusat kota. Target/labelnya adalah harga rumah.",
    },
    {
        "subject": "umum",
        "trigger_text": "konsep stabil web search gagal definisi materi pelajaran",
        "correction": "Jika web search gagal untuk pertanyaan konsep stabil, definisi, materi pelajaran, coding umum, atau matematika, tetap jawab dari pengetahuan umum dan konteks pemeriksaan. Jangan menjawab hanya 'tidak menemukan hasil'.",
    },
    {
        "subject": "umum",
        "trigger_text": "jawaban konsep teknis ai ml berkualitas tinggi",
        "correction": "Untuk konsep teknis AI/ML, jawab dengan pola: definisi singkat, fungsi dalam sistem, contoh konkret, bedakan dengan istilah mirip, lalu catatan penting agar tidak salah paham.",
    },
    {
        "subject": "umum",
        "trigger_text": "label target feature dataset supervised learning",
        "correction": "Bedakan feature dan label/target. Feature adalah input model, label/target adalah output yang ingin diprediksi. Dataset berisi banyak baris contoh, setiap baris memiliki feature dan bisa memiliki label jika supervised learning.",
    },
    {
        "subject": "umum",
        "trigger_text": "ranking terbaru harga berita tahun ini data berubah",
        "correction": "Untuk data terbaru seperti ranking, harga, berita, jadwal, atau kondisi yang berubah, gunakan web search jika aktif. Jika tidak ada konteks web search, katakan perlu dicek dari sumber terbaru.",
    },
    {
        "subject": "umum",
        "trigger_text": "pertanyaan menjebak premis salah",
        "correction": "Cek premis sebelum menjawab. Jika premis keliru, koreksi dengan sopan dan jangan mengikuti asumsi yang salah.",
    },
    {
        "subject": "matematika",
        "trigger_text": "rasio awal rasio akhir total akhir perubahan",
        "correction": "Aktifkan deep_check_mode. Gunakan variabel untuk kondisi awal, bentuk kondisi akhir setelah perubahan, buat persamaan total/rasio akhir, lalu validasi semua syarat.",
    },
    {
        "subject": "matematika",
        "trigger_text": "perbandingan menjadi mula mula setelah transfer",
        "correction": "Jika ada rasio awal dan rasio akhir, jangan memakai variabel yang sama sembarangan. Terapkan perubahan hanya pada pihak yang disebut berubah. Pada transfer, pemberi berkurang dan penerima bertambah.",
    },
    {
        "subject": "matematika",
        "trigger_text": "total akhir rasio awal setelah perubahan",
        "correction": "Jangan membagi total akhir memakai rasio awal jika ada perubahan. Bentuk persamaan dari kondisi akhir dan cek konsistensi total akhir.",
    },
    {
        "subject": "matematika",
        "trigger_text": "soal cerita matematika uang orang barang",
        "correction": "Baca semua kalimat. Catat diketahui, ditanya, kondisi awal, perubahan, kondisi akhir, lalu cek apakah jawaban memenuhi semua kondisi.",
    },
    {
        "subject": "matematika",
        "trigger_text": "pecahan desimal pembulatan persen",
        "correction": "Jangan membulatkan terlalu awal. Simpan pecahan atau presisi tinggi sampai akhir. Jika benda hitungan menghasilkan desimal, beri catatan bahwa datanya mungkin tidak ideal.",
    },
    {
        "subject": "matematika",
        "trigger_text": "persamaan aljabar nilai x",
        "correction": "Tulis langkah operasi kebalikan, jaga tanda positif/negatif, lalu cek hasil dengan substitusi ke persamaan awal.",
    },
    {
        "subject": "matematika",
        "trigger_text": "limit turunan integral fungsi",
        "correction": "Tentukan domain dan metode. Untuk turunan/integral, sebutkan aturan yang dipakai, jangan lompat langkah penting, dan cek hasil jika memungkinkan.",
    },
    {
        "subject": "fisika",
        "trigger_text": "gaya massa percepatan kecepatan waktu",
        "correction": "F/m adalah percepatan, bukan kecepatan. Jika ditanya kecepatan setelah t detik dari diam, hitung a = F / m lalu v = a x t.",
    },
    {
        "subject": "fisika",
        "trigger_text": "fisika satuan dimensi si",
        "correction": "Konversi ke satuan SI, tulis satuan setiap besaran, dan cek dimensi jawaban akhir sebelum menyimpulkan.",
    },
    {
        "subject": "fisika",
        "trigger_text": "energi usaha daya momentum",
        "correction": "Bedakan energi, usaha, daya, dan momentum. Pilih hukum kekekalan atau rumus kerja sesuai kondisi soal, bukan hanya dari kata kunci.",
    },
    {
        "subject": "fisika",
        "trigger_text": "gerak lurus glb glbb percepatan",
        "correction": "Tentukan apakah GLB atau GLBB. Cek kecepatan awal, waktu, percepatan, dan jarak. Jangan memakai rumus GLB untuk gerak berubah beraturan.",
    },
    {
        "subject": "kimia",
        "trigger_text": "mol massa mr stoikiometri",
        "correction": "Gunakan n = massa / Mr, setarakan reaksi dulu, pakai perbandingan koefisien, dan cek pereaksi pembatas jika ada lebih dari satu reaktan.",
    },
    {
        "subject": "kimia",
        "trigger_text": "asam basa ph poh",
        "correction": "Cek kuat/lemah asam-basa, konsentrasi, dan hubungan pH/pOH. Jangan mencampur pH dengan pOH.",
    },
    {
        "subject": "kimia",
        "trigger_text": "reaksi oksidasi reduksi redoks",
        "correction": "Tentukan bilangan oksidasi, siapa teroksidasi/tereduksi, oksidator/reduktor, lalu setarakan reaksi jika diperlukan.",
    },
    {
        "subject": "kimia",
        "trigger_text": "larutan konsentrasi molaritas pengenceran",
        "correction": "Pastikan volume dalam liter, konsentrasi dalam mol/L, dan gunakan M1V1 = M2V2 hanya untuk pengenceran yang sesuai.",
    },
    {
        "subject": "bahasa_inggris",
        "trigger_text": "grammar subject verb agreement",
        "correction": "Cari subject utama dan verb utama. Frasa sisipan tidak mengubah jumlah subject utama.",
    },
    {
        "subject": "bahasa_inggris",
        "trigger_text": "tenses kalimat verb time marker",
        "correction": "Cek time marker, bentuk verb, auxiliary, dan konsistensi tense sebelum memilih jawaban.",
    },
    {
        "subject": "bahasa_inggris",
        "trigger_text": "vocabulary synonym antonym context",
        "correction": "Gunakan konteks kalimat. Jangan memilih arti kamus jika tidak cocok dengan konteks.",
    },
    {
        "subject": "toefl",
        "trigger_text": "toefl structure written expression",
        "correction": "Gunakan eliminasi. Cari subject, verb, modifier, parallelism, pronoun reference, dan error agreement.",
    },
    {
        "subject": "toefl",
        "trigger_text": "toefl reading comprehension passage",
        "correction": "Jawab berdasarkan evidence di passage. Jangan memakai asumsi luar teks. Jika tidak ada bukti, katakan tidak ditemukan dalam teks.",
    },
    {
        "subject": "toefl",
        "trigger_text": "toefl vocabulary closest meaning",
        "correction": "Tentukan makna kata dari konteks sekitar, bukan hanya arti paling umum. Eliminasi opsi yang tidak cocok dengan nada kalimat.",
    },
    {
        "subject": "sejarah",
        "trigger_text": "tanggal tokoh peristiwa sejarah",
        "correction": "Jawab dengan tanggal, tokoh, dan peristiwa spesifik jika faktanya stabil. Jika tidak yakin, nyatakan belum bisa memastikan.",
    },
    {
        "subject": "sejarah",
        "trigger_text": "sebab akibat peristiwa sejarah",
        "correction": "Bedakan sebab utama, pemicu, proses, dan dampak. Jangan mencampur konteks waktu atau tokoh.",
    },
    {
        "subject": "sejarah",
        "trigger_text": "proklamasi indonesia kemerdekaan",
        "correction": "Untuk Proklamasi Indonesia, fakta stabil: 17 Agustus 1945, dibacakan oleh Soekarno didampingi Mohammad Hatta di Jakarta.",
    },
    {
        "subject": "pendidikan",
        "trigger_text": "pedagogik kurikulum pembelajaran asesmen",
        "correction": "Bedakan tujuan pembelajaran, metode, media, asesmen formatif/sumatif, dan evaluasi hasil belajar.",
    },
    {
        "subject": "pendidikan",
        "trigger_text": "evaluasi jawaban siswa rubrik",
        "correction": "Saat mengevaluasi jawaban siswa, bandingkan dengan indikator, konsep inti, dan rubrik sederhana. Jelaskan benar, salah, atau sebagian benar.",
    },
    {
        "subject": "coding",
        "trigger_text": "buat aplikasi python project",
        "correction": "Jangan memberi kode toy. Berikan struktur folder, arsitektur, kode per file, cara menjalankan, cara test, dan catatan pengembangan.",
    },
    {
        "subject": "coding",
        "trigger_text": "rename file otomatis",
        "correction": "Wajib ada argparse, pathlib, dry-run, collision handling, log operasi, undo dari log, validasi path, dan pytest.",
    },
    {
        "subject": "coding",
        "trigger_text": "flask sqlite crud",
        "correction": "Pisahkan route, database, template/static, validasi input, error handling, init_db, dan contoh test minimal.",
    },
    {
        "subject": "coding",
        "trigger_text": "debug error traceback bug",
        "correction": "Baca traceback dari bawah, identifikasi file/baris, jelaskan akar masalah, lalu beri patch minimal dan cara verifikasi.",
    },
    {
        "subject": "coding",
        "trigger_text": "security file upload path",
        "correction": "Validasi ekstensi, ukuran file, nama file aman, jangan percaya input user mentah, dan cegah path traversal.",
    },
    {
        "subject": "coding",
        "trigger_text": "test pytest unit integration",
        "correction": "Sertakan test untuk fungsi inti, edge case, dan error path. Jelaskan command pytest.",
    },
    {
        "subject": "coding",
        "trigger_text": "refactor kode modular",
        "correction": "Pisahkan logic menjadi fungsi kecil, hindari global state berlebihan, gunakan type hints bila membantu, dan jaga backward compatibility.",
    },
]


ADVANCED_TRAINING_NOTES = [
    (
        "umum",
        "jawaban terlalu panjang membingungkan",
        "Jawab dengan struktur pendek: inti jawaban, alasan utama, langkah penting, lalu kesimpulan. Hindari paragraf panjang tanpa jeda.",
    ),
    (
        "umum",
        "jawaban ragu fakta penting",
        "Jika fakta penting tidak yakin, jangan isi dengan tebakan. Tulis: Saya belum bisa memastikan karena data belum cukup.",
    ),
    (
        "umum",
        "pertanyaan banyak syarat multi syarat",
        "Pisahkan setiap syarat menjadi daftar. Jawaban akhir harus memenuhi semua syarat, bukan hanya syarat yang paling mudah.",
    ),
    (
        "umum",
        "evaluasi jawaban benar salah",
        "Bandingkan jawaban dengan pertanyaan asli berdasarkan objek, jumlah, waktu, tempat, tindakan, dan alasan. Lalu beri status benar/salah/sebagian benar.",
    ),
    (
        "umum",
        "minta ringkas rangkuman",
        "Buat ringkasan berdasarkan poin utama, bukan menyalin semua kalimat. Bedakan ide pokok, detail pendukung, dan kesimpulan.",
    ),
    (
        "umum",
        "minta ide rencana strategi",
        "Berikan ide yang praktis dan bisa dilakukan. Jika ada risiko atau keterbatasan, tulis catatan singkat.",
    ),
    (
        "umum",
        "membandingkan dua pilihan",
        "Gunakan tabel ringkas bila membantu. Bandingkan berdasarkan kriteria yang sama agar tidak bias.",
    ),
    (
        "umum",
        "instruksi admin format tertentu",
        "Ikuti format yang diminta Admin. Jangan mengganti format, jumlah poin, nama, atau objek yang diberikan.",
    ),
    (
        "umum",
        "data dokumen file pdf",
        "Jika ada konteks dokumen/PDF, jawab berdasarkan dokumen. Jika informasi tidak ada, katakan informasi itu tidak ditemukan dalam data yang diberikan.",
    ),
    (
        "umum",
        "pertanyaan definisi konsep",
        "Berikan definisi singkat, contoh sederhana, lalu bedakan dengan konsep yang mirip jika rawan tertukar.",
    ),
    (
        "matematika",
        "persentase diskon untung rugi",
        "Tentukan nilai awal, perubahan persen, dan nilai akhir. Jangan mencampur persen dari modal dengan persen dari harga jual.",
    ),
    (
        "matematika",
        "bunga tunggal bunga majemuk",
        "Bedakan bunga tunggal dan bunga majemuk. Tulis rumus, periode, suku bunga, lalu cek apakah persen per tahun/bulan sesuai.",
    ),
    (
        "matematika",
        "skala peta perbandingan jarak",
        "Samakan satuan dulu. Gunakan skala sebagai jarak peta : jarak sebenarnya, lalu cek konversi cm, m, dan km.",
    ),
    (
        "matematika",
        "kecepatan jarak waktu",
        "Gunakan jarak = kecepatan x waktu. Samakan satuan jam/menit/detik sebelum menghitung.",
    ),
    (
        "matematika",
        "sistem persamaan linear spldv",
        "Definisikan variabel, bentuk dua persamaan, selesaikan eliminasi/substitusi, lalu cek kedua persamaan.",
    ),
    (
        "matematika",
        "fungsi kuadrat akar diskriminan",
        "Cek a, b, c, diskriminan, akar, titik puncak, dan arah parabola. Jangan salah tanda saat memakai -b/(2a).",
    ),
    (
        "matematika",
        "barisan aritmetika geometri",
        "Bedakan beda tetap dan rasio tetap. Tentukan suku pertama, beda/rasio, indeks suku, lalu gunakan rumus yang sesuai.",
    ),
    (
        "matematika",
        "kombinasi permutasi peluang",
        "Tentukan apakah urutan penting. Gunakan permutasi jika urutan penting, kombinasi jika urutan tidak penting.",
    ),
    (
        "matematika",
        "probabilitas peluang kejadian",
        "Tentukan ruang sampel dan kejadian. Untuk kejadian gabungan, cek apakah saling lepas atau independen.",
    ),
    (
        "matematika",
        "trigonometri sin cos tan",
        "Cek kuadran, tanda sin/cos/tan, identitas trigonometri, dan satuan derajat/radian.",
    ),
    (
        "matematika",
        "logaritma eksponen",
        "Cek basis log harus positif dan tidak sama dengan 1. Gunakan sifat log dengan hati-hati dan cek domain.",
    ),
    (
        "matematika",
        "geometri luas volume",
        "Tulis bentuk bangun, rumus, satuan kuadrat/kubik, dan cek apakah tinggi/jari-jari/diameter sudah benar.",
    ),
    (
        "matematika",
        "statistika mean median modus",
        "Urutkan data jika mencari median. Bedakan mean, median, modus, kuartil, dan cek jumlah data ganjil/genap.",
    ),
    (
        "matematika",
        "matriks determinan invers",
        "Cek ukuran matriks. Determinan/invers hanya berlaku untuk matriks persegi; invers ada jika determinan tidak nol.",
    ),
    (
        "matematika",
        "pembuktian induksi matematika",
        "Gunakan basis induksi, asumsi induksi, langkah induksi, lalu kesimpulan. Jangan langsung menganggap benar untuk semua n.",
    ),
    (
        "matematika",
        "soal tidak konsisten matematika",
        "Jika dua persamaan/syarat menghasilkan nilai berbeda untuk variabel yang sama, nyatakan data tidak konsisten dan tidak ada solusi yang memenuhi semua syarat.",
    ),
    (
        "fisika",
        "resultan gaya bidang datar",
        "Gambar gaya secara mental, pilih arah positif, jumlahkan gaya searah positif dan negatif, lalu gunakan resultan gaya.",
    ),
    (
        "fisika",
        "gaya gesek koefisien normal",
        "Gaya gesek f = mu x N. Di bidang datar N = mg jika tidak ada gaya vertikal lain. Cek statis/kinetis.",
    ),
    (
        "fisika",
        "hukum newton katrol tegangan tali",
        "Buat persamaan gaya untuk tiap benda. Tegangan tali sama hanya jika tali/katrol ideal.",
    ),
    (
        "fisika",
        "usaha energi kinetik potensial",
        "Gunakan teorema usaha-energi jika cocok. Energi potensial gravitasi mgh perlu acuan ketinggian yang jelas.",
    ),
    (
        "fisika",
        "momentum impuls tumbukan",
        "Momentum p = m x v, impuls = perubahan momentum. Cek arah kecepatan karena momentum adalah vektor.",
    ),
    (
        "fisika",
        "listrik arus tegangan hambatan",
        "Gunakan V = I x R. Cek rangkaian seri/paralel sebelum mencari hambatan total.",
    ),
    (
        "fisika",
        "daya listrik energi listrik",
        "Bedakan daya dan energi. P = V x I atau P = I^2R; energi = P x t dengan satuan waktu konsisten.",
    ),
    (
        "fisika",
        "gelombang frekuensi periode panjang gelombang",
        "Gunakan v = lambda x f dan T = 1/f. Jangan tertukar antara periode dan frekuensi.",
    ),
    (
        "fisika",
        "suhu kalor perubahan wujud",
        "Gunakan Q = m c deltaT untuk perubahan suhu dan Q = m L untuk perubahan wujud. Jangan pakai keduanya tanpa alasan.",
    ),
    (
        "fisika",
        "tekanan hidrostatis fluida",
        "Gunakan P = rho g h untuk tekanan hidrostatis. Kedalaman dihitung dari permukaan cairan, bukan dari dasar.",
    ),
    (
        "fisika",
        "optik lensa cermin",
        "Gunakan 1/f = 1/s + 1/s'. Cek tanda sesuai konvensi dan bedakan bayangan nyata/maya.",
    ),
    (
        "kimia",
        "persamaan reaksi setara",
        "Setarakan jumlah atom kiri dan kanan sebelum menghitung mol atau massa. Jangan mengubah indeks senyawa.",
    ),
    (
        "kimia",
        "pereaksi pembatas hasil reaksi",
        "Hitung mol tiap reaktan, bandingkan terhadap koefisien reaksi, tentukan pereaksi pembatas, lalu hitung produk.",
    ),
    (
        "kimia",
        "konsentrasi molaritas molalitas",
        "Molaritas memakai volume larutan dalam liter, molalitas memakai massa pelarut dalam kg.",
    ),
    (
        "kimia",
        "larutan penyangga buffer",
        "Untuk buffer, identifikasi asam lemah/basa lemah dan pasangan konjugasinya. Gunakan Henderson-Hasselbalch jika datanya cocok.",
    ),
    (
        "kimia",
        "hidrolisis garam",
        "Tentukan asal garam dari asam kuat/lemah dan basa kuat/lemah, lalu prediksi sifat larutan.",
    ),
    (
        "kimia",
        "kesetimbangan kc kp",
        "Tulis ekspresi K hanya dari zat gas/larutan, abaikan padatan/cairan murni, dan gunakan pangkat koefisien.",
    ),
    (
        "kimia",
        "termokimia delta h",
        "Perhatikan tanda delta H: eksoterm negatif, endoterm positif. Sesuaikan jika reaksi dibalik atau dikalikan.",
    ),
    (
        "kimia",
        "struktur atom konfigurasi elektron",
        "Tulis konfigurasi elektron berdasarkan urutan orbital dan cek jumlah elektron sesuai nomor atom/ion.",
    ),
    (
        "kimia",
        "ikatan ion kovalen polar",
        "Tentukan jenis ikatan dari unsur penyusun dan perbedaan elektronegativitas. Cek bentuk molekul untuk polaritas.",
    ),
    (
        "bahasa_inggris",
        "passive voice active voice",
        "Cek objek kalimat aktif menjadi subject kalimat pasif. Gunakan be + V3 dan pertahankan tense.",
    ),
    (
        "bahasa_inggris",
        "conditional sentence if clause",
        "Identifikasi tipe conditional dari tense if-clause dan main clause. Jangan mencampur type 1, 2, dan 3.",
    ),
    (
        "bahasa_inggris",
        "relative clause who which that",
        "Gunakan who untuk orang, which untuk benda/hewan, that bisa untuk restrictive clause. Cek apakah clause membatasi atau hanya tambahan.",
    ),
    (
        "bahasa_inggris",
        "gerund infinitive verb pattern",
        "Cek pola verb yang diikuti gerund atau infinitive. Jangan memilih bentuk hanya karena terdengar natural.",
    ),
    (
        "bahasa_inggris",
        "parallel structure",
        "Dalam daftar atau pasangan conjunction, bentuk kata harus paralel: noun dengan noun, verb dengan verb, adjective dengan adjective.",
    ),
    (
        "bahasa_inggris",
        "pronoun reference",
        "Cek pronoun merujuk ke noun yang jelas dan cocok jumlah/gendernya. Hindari rujukan ambigu.",
    ),
    (
        "bahasa_inggris",
        "reading main idea inference",
        "Untuk main idea, pilih opsi yang mencakup seluruh paragraf. Untuk inference, harus didukung teks meski tidak tertulis langsung.",
    ),
    (
        "toefl",
        "toefl sentence completion",
        "Cari struktur kalimat yang belum lengkap: subject, verb, complement, modifier. Pilih opsi yang melengkapi grammar, bukan hanya makna.",
    ),
    (
        "toefl",
        "toefl error identification",
        "Periksa satu per satu: subject-verb agreement, tense, word form, parallelism, preposition, article, and pronoun reference.",
    ),
    (
        "toefl",
        "toefl stated detail question",
        "Cari kata kunci di passage, cocokkan sinonim/parafrase, dan hindari opsi yang terlalu luas atau bertentangan.",
    ),
    (
        "toefl",
        "toefl unstated except not",
        "Untuk soal EXCEPT/NOT, cari opsi yang tidak disebut atau bertentangan. Tandai bahwa pertanyaannya negatif.",
    ),
    (
        "toefl",
        "toefl transition connector",
        "Cek hubungan ide: cause-effect, contrast, addition, result, condition. Pilih connector sesuai hubungan logis.",
    ),
    (
        "sejarah",
        "kronologi urutan peristiwa",
        "Susun peristiwa berdasarkan waktu. Jangan membalik sebab dan akibat karena urutan sejarah penting.",
    ),
    (
        "sejarah",
        "tokoh peran kontribusi",
        "Sebutkan tokoh, peran spesifik, konteks waktu, dan dampaknya. Jangan melebihkan peran jika tidak didukung fakta.",
    ),
    (
        "sejarah",
        "kolonialisme imperialisme indonesia",
        "Bedakan kolonialisme, imperialisme, monopoli perdagangan, tanam paksa, politik etis, dan dampaknya.",
    ),
    (
        "sejarah",
        "revolusi perang perjanjian",
        "Cek pihak yang terlibat, sebab, proses, hasil perjanjian, dan dampak jangka pendek/panjang.",
    ),
    (
        "pendidikan",
        "tujuan pembelajaran indikator capaian",
        "Bedakan capaian pembelajaran, tujuan pembelajaran, indikator, aktivitas, dan asesmen. Semuanya harus selaras.",
    ),
    (
        "pendidikan",
        "metode pembelajaran problem based learning project based learning",
        "Bedakan PBL berbasis masalah dan PjBL berbasis proyek/produk. Sesuaikan metode dengan tujuan dan karakter siswa.",
    ),
    (
        "pendidikan",
        "asesmen formatif sumatif diagnostik",
        "Asesmen diagnostik untuk awal, formatif selama proses, sumatif di akhir. Jangan mencampur fungsi asesmen.",
    ),
    (
        "pendidikan",
        "diferensiasi pembelajaran",
        "Diferensiasi bisa pada konten, proses, produk, atau lingkungan belajar. Sesuaikan dengan kesiapan, minat, dan profil belajar siswa.",
    ),
    (
        "pendidikan",
        "rubrik penilaian",
        "Rubrik harus punya kriteria, level performa, dan deskripsi tiap level. Hindari penilaian yang hanya subjektif.",
    ),
    (
        "coding",
        "buat aplikasi cli python",
        "Untuk CLI Python, gunakan argparse, fungsi main, validasi input, kode modular, pesan error jelas, dan contoh command.",
    ),
    (
        "coding",
        "buat aplikasi web flask",
        "Untuk Flask app, pisahkan app, database/service, templates, static, validasi form, flash error, dan route yang jelas.",
    ),
    (
        "coding",
        "buat api rest python",
        "Untuk REST API, definisikan endpoint, method, payload JSON, validasi input, status code, error response, dan contoh curl.",
    ),
    (
        "coding",
        "buat aplikasi desktop tkinter",
        "Untuk Tkinter, pisahkan UI, state, handler, dan logic. Jangan menaruh semua logic di callback panjang.",
    ),
    (
        "coding",
        "python sqlite database",
        "Gunakan parameterized query, context manager, init schema, fungsi repository kecil, dan jangan membuat query dari string input mentah.",
    ),
    (
        "coding",
        "python file handling csv json",
        "Gunakan pathlib, encoding utf-8, error handling, dan validasi format file. Jangan menimpa file tanpa backup/dry-run jika data penting.",
    ),
    (
        "coding",
        "aplikasi automation batch file",
        "Untuk automasi Windows, jelaskan risiko, gunakan path aman, cek file/folder ada, dan jangan hapus/move massal tanpa konfirmasi.",
    ),
    (
        "coding",
        "logging monitoring error handling",
        "Tambahkan logging yang berguna, bukan print acak. Error handling harus memberi pesan jelas dan tidak menyembunyikan bug penting.",
    ),
    (
        "coding",
        "desain arsitektur software",
        "Jelaskan komponen, alur data, boundary module, dependency, penyimpanan data, dan trade-off. Hindari arsitektur berlebihan untuk MVP.",
    ),
    (
        "coding",
        "clean code python",
        "Gunakan nama fungsi jelas, fungsi kecil, return eksplisit, type hints bila membantu, dan hindari duplikasi logic.",
    ),
    (
        "coding",
        "algoritma struktur data",
        "Jelaskan ide algoritma, kompleksitas waktu/ruang, edge case, lalu berikan implementasi yang bisa diuji.",
    ),
    (
        "coding",
        "web html css javascript",
        "Pisahkan HTML, CSS, JS. Pastikan responsive, aksesibilitas dasar, validasi input, dan event listener tidak duplikat.",
    ),
    (
        "coding",
        "javascript fetch api async",
        "Gunakan async/await, tangani loading/error, cek response.ok, dan jangan membekukan UI saat request berjalan.",
    ),
    (
        "coding",
        "security authentication password",
        "Jangan simpan password plain text. Untuk MVP tanpa login, jelaskan bahwa auth belum dibuat. Untuk auth, gunakan hashing aman dan session.",
    ),
    (
        "coding",
        "deployment local production",
        "Bedakan mode development dan production. Jelaskan env var, debug off, dependency, database path, dan cara menjalankan.",
    ),
    (
        "coding",
        "review kode bug risiko",
        "Saat review kode, prioritaskan bug, risiko regresi, celah keamanan, dan test yang kurang. Beri referensi baris bila ada.",
    ),
]

def _build_bulk_training_notes() -> list[dict]:
    subject_topics = {
        "umum": [
            "data terbaru", "pertanyaan ambigu", "jawaban singkat", "ringkasan", "perbandingan pilihan",
            "rencana belajar", "ide kreatif", "jadwal harian", "evaluasi jawaban", "dokumen pdf",
            "fakta umum", "definisi konsep", "argumen pro kontra", "instruksi bertahap", "analisis risiko",
            "data kurang", "pertanyaan menjebak", "sumber informasi",
        ],
        "matematika": [
            "aljabar", "persamaan linear", "sistem persamaan", "persamaan kuadrat", "fungsi kuadrat",
            "rasio", "perbandingan", "persentase", "untung rugi", "bunga majemuk", "skala peta",
            "kecepatan jarak waktu", "barisan aritmetika", "barisan geometri", "deret", "peluang",
            "kombinasi", "permutasi", "statistika", "mean median modus", "geometri datar",
            "geometri ruang", "trigonometri", "logaritma", "eksponen", "limit", "turunan",
            "integral", "matriks", "determinan", "vektor", "induksi matematika", "pembuktian",
            "soal cerita uang", "validasi konsistensi",
        ],
        "fisika": [
            "hukum newton", "resultan gaya", "gaya gesek", "gerak lurus", "glb", "glbb",
            "gerak parabola", "usaha energi", "energi kinetik", "energi potensial", "daya",
            "momentum impuls", "tumbukan", "tekanan", "fluida", "hidrostatis", "kalor",
            "suhu", "gelombang", "bunyi", "cahaya", "lensa", "cermin", "listrik dinamis",
            "hukum ohm", "rangkaian seri paralel", "medan magnet", "induksi", "dimensi satuan",
            "grafik gerak",
        ],
        "kimia": [
            "mol", "massa molar", "stoikiometri", "persamaan reaksi", "pereaksi pembatas",
            "asam basa", "ph", "poh", "larutan", "molaritas", "molalitas", "pengenceran",
            "redoks", "bilangan oksidasi", "elektrokimia", "kesetimbangan", "kc kp",
            "larutan penyangga", "hidrolisis garam", "termokimia", "entalpi", "laju reaksi",
            "struktur atom", "konfigurasi elektron", "ikatan kimia", "bentuk molekul",
            "kimia organik dasar", "polimer",
        ],
        "bahasa_inggris": [
            "subject verb agreement", "tenses", "passive voice", "active voice", "conditional sentence",
            "relative clause", "gerund infinitive", "parallel structure", "pronoun reference",
            "preposition", "article", "word form", "vocabulary context", "synonym antonym",
            "reading main idea", "reading inference", "error correction", "sentence structure",
            "reported speech", "comparison degree", "modal auxiliary", "conjunction",
            "paragraph writing", "grammar explanation",
        ],
        "toefl": [
            "structure", "written expression", "reading comprehension", "vocabulary", "error recognition",
            "sentence completion", "main idea", "stated detail", "unstated detail", "except question",
            "inference", "reference question", "transition connector", "parallelism", "inversion",
            "reduced clause", "appositive", "modifier", "word form", "time management",
        ],
        "sejarah": [
            "kronologi", "tokoh sejarah", "sebab akibat", "proklamasi indonesia", "kolonialisme",
            "imperialisme", "voc", "tanam paksa", "politik etis", "pergerakan nasional",
            "sumpah pemuda", "bpupki ppki", "revolusi kemerdekaan", "perjanjian sejarah",
            "orde lama", "orde baru", "reformasi", "kerajaan hindu buddha", "kerajaan islam",
            "perang dunia", "perang dingin", "asean", "pbb", "dampak peristiwa",
        ],
        "pendidikan": [
            "pedagogik", "kurikulum", "tujuan pembelajaran", "capaian pembelajaran", "indikator",
            "metode pembelajaran", "model pbl", "model pjbl", "asesmen diagnostik", "asesmen formatif",
            "asesmen sumatif", "rubrik penilaian", "diferensiasi", "media pembelajaran",
            "evaluasi pembelajaran", "karakter siswa", "motivasi belajar", "manajemen kelas",
            "literasi numerasi", "rpp modul ajar", "refleksi guru", "remedial pengayaan",
        ],
        "coding": [
            "python cli", "python oop", "python file handling", "python csv json", "python sqlite",
            "flask app", "flask sqlite", "rest api", "crud", "authentication", "file upload",
            "web scraping", "automation", "rename file", "batch windows", "tkinter desktop",
            "html css", "javascript fetch", "async request", "debug traceback", "pytest",
            "unit test", "integration test", "logging", "error handling", "security input",
            "path traversal", "clean code", "refactor", "architecture", "deployment local",
            "configuration env", "database migration", "frontend responsive", "copy code block",
            "documentation",
        ],
    }

    study_templates = [
        (
            "konsep dasar",
            "Untuk topik {topic}, mulai dari konsep inti, syarat pemakaian rumus/aturan, contoh pendek, lalu cek apakah pertanyaan Admin meminta definisi, hitungan, atau evaluasi.",
        ),
        (
            "soal pilihan ganda",
            "Untuk pilihan ganda {topic}, baca stem dulu, eliminasi opsi salah, waspadai kata ekstrem, lalu jelaskan singkat kenapa opsi benar dan opsi lain salah.",
        ),
        (
            "soal menjebak",
            "Untuk soal menjebak {topic}, cek premis, satuan, kondisi awal/akhir, kata pengecualian, dan jangan menyimpulkan sebelum validasi.",
        ),
        (
            "soal cerita",
            "Untuk soal cerita {topic}, tulis diketahui, ditanya, perubahan, model/persamaan, langkah, cek ulang, dan jawaban akhir.",
        ),
        (
            "evaluasi jawaban",
            "Saat mengevaluasi jawaban pada {topic}, bandingkan dengan soal asli, tunjukkan kesalahan utama, detail yang berubah, dan versi jawaban yang benar.",
        ),
        (
            "latihan advanced",
            "Jika Admin meminta latihan {topic}, buat soal bertahap dari dasar ke sulit, berikan kunci, dan sertakan satu catatan jebakan umum.",
        ),
        (
            "ringkasan materi",
            "Untuk merangkum {topic}, ambil ide pokok, rumus/aturan penting, contoh aplikasi, dan kesalahan umum. Jangan menambah fakta yang tidak ada di teks.",
        ),
        (
            "kesalahan umum",
            "Sebelum menjawab {topic}, cek kesalahan umum: salah membaca pertanyaan, salah satuan, salah objek, salah tanda, atau memakai rumus yang tidak sesuai.",
        ),
        (
            "langkah penyelesaian",
            "Untuk penyelesaian {topic}, buat langkah bernomor pendek. Setiap langkah harus punya alasan, bukan hanya operasi hitung atau klaim.",
        ),
        (
            "cek ulang",
            "Setelah menjawab {topic}, lakukan cek ulang singkat terhadap data soal. Jika hasil tidak memenuhi syarat, revisi atau nyatakan data tidak konsisten.",
        ),
    ]

    coding_templates = [
        (
            "kebutuhan aplikasi",
            "Untuk permintaan coding {topic}, klarifikasi asumsi, tulis fitur utama, batasan, struktur folder, lalu kode siap jalan.",
        ),
        (
            "kode per file",
            "Untuk project {topic}, pisahkan kode per file dengan judul path file dan fenced code block agar tombol Copy muncul.",
        ),
        (
            "error handling",
            "Untuk {topic}, tambahkan validasi input, pesan error ramah, dan hindari crash tanpa penjelasan.",
        ),
        (
            "testing",
            "Untuk {topic}, sertakan test pytest atau minimal cara uji manual yang jelas, termasuk edge case.",
        ),
        (
            "security",
            "Untuk {topic}, cek risiko input user, path traversal, overwrite file, injection, dan data sensitif.",
        ),
        (
            "debugging",
            "Saat debugging {topic}, baca traceback dari bawah, cari akar masalah, beri patch minimal, lalu cara verifikasi.",
        ),
        (
            "arsitektur",
            "Untuk aplikasi {topic}, jelaskan alur data, modul, penyimpanan, konfigurasi, dan trade-off tanpa membuat sistem berlebihan.",
        ),
        (
            "dokumentasi",
            "Untuk {topic}, sertakan cara install dependency, cara menjalankan, contoh input, dan pengembangan berikutnya.",
        ),
        (
            "kualitas kode",
            "Untuk {topic}, gunakan fungsi kecil, nama jelas, type hints bila membantu, logging, dan hindari kode toy.",
        ),
        (
            "fitur lengkap",
            "Jika Admin meminta aplikasi {topic}, jangan berhenti di contoh sederhana. Beri versi fungsional dengan validasi, penyimpanan bila perlu, dan test.",
        ),
    ]

    notes = []
    for subject, topics in subject_topics.items():
        templates = coding_templates if subject == "coding" else study_templates
        for topic in topics:
            for intent, correction in templates:
                notes.append(
                    {
                        "subject": subject,
                        "trigger_text": f"{topic} {intent}",
                        "correction": correction.format(topic=topic),
                    }
                )
    return notes


BULK_TRAINING_NOTES = _build_bulk_training_notes()


def _build_mega_training_notes(base_notes: list[dict]) -> list[dict]:
    quality_dimensions = [
        ("akurasi fakta", "cek apakah fakta, tanggal, nama, dan istilah sesuai dengan konteks terbaru atau data yang diberikan."),
        ("anti halusinasi", "jangan menambahkan angka, sumber, tokoh, atau detail yang tidak ada dasar datanya."),
        ("validasi syarat", "cek semua syarat satu per satu sebelum membuat kesimpulan akhir."),
        ("jawaban rapi", "jawab dengan format pendek, jelas, dan tidak membuat Admin pusing."),
        ("contoh relevan", "beri contoh yang langsung terkait pertanyaan, bukan contoh umum yang melebar."),
        ("kesalahan umum", "sebutkan jebakan paling mungkin dan cara menghindarinya."),
        ("cek ulang akhir", "uji kembali jawaban terhadap pertanyaan asli sebelum menutup jawaban."),
        ("level advanced", "gunakan penalaran lebih dalam, jelaskan asumsi, dan jangan menyederhanakan masalah secara keliru."),
    ]
    levels = [
        ("dasar", "pastikan konsep inti benar dan mudah dipahami."),
        ("menengah", "tambahkan hubungan antar konsep dan langkah pemeriksaan."),
        ("sulit", "pecah masalah menjadi bagian kecil dan cek setiap bagian."),
        ("menjebak", "curigai premis, kata pengecualian, satuan, dan perubahan kondisi."),
    ]

    notes = []
    for note in base_notes:
        base_trigger = note["trigger_text"]
        subject = note["subject"]
        for dimension, dimension_rule in quality_dimensions:
            for level, level_rule in levels:
                notes.append(
                    {
                        "subject": subject,
                        "trigger_text": f"{base_trigger} {dimension} {level}",
                        "correction": (
                            f"Untuk topik '{base_trigger}', mode {level}: {dimension_rule} "
                            f"{level_rule} Jika hasil bertentangan dengan data soal atau sumber, revisi jawaban."
                        ),
                    }
                )
    return notes


MEGA_TRAINING_NOTES = _build_mega_training_notes(BULK_TRAINING_NOTES)


def _build_ultra_training_notes(base_notes: list[dict]) -> list[dict]:
    ultra_rules = [
        ("jawaban terbaik", "beri jawaban paling langsung dulu, lalu sumber/cek ulang seperlunya."),
        ("anti data lama", "untuk data saat ini, jangan memakai data lama jika ada konteks web/trusted source."),
        ("sumber resmi", "prioritaskan sumber resmi, institusi kredibel, atau dokumen yang diberikan Admin."),
    ]

    notes = []
    for note in base_notes:
        for label, rule in ultra_rules:
            notes.append(
                {
                    "subject": note["subject"],
                    "trigger_text": f"{note['trigger_text']} {label}",
                    "correction": f"Ultra training untuk '{note['trigger_text']}': {rule} Jika ragu, nyatakan keterbatasan dengan jelas tanpa mengarang.",
                }
            )
    return notes


ULTRA_TRAINING_NOTES = _build_ultra_training_notes(MEGA_TRAINING_NOTES)


def _build_hyper_training_notes(base_notes: list[dict]) -> list[dict]:
    hyper_rules = [
        ("gaya santai", "jawab seperti teman belajar yang sopan: natural, ringan, dan tidak kaku, tetapi tetap akurat."),
        ("inti dulu", "beri inti jawaban di awal agar Admin tidak perlu menebak arah jawaban."),
        ("anti ngaco", "jika data tidak cukup, jangan mengisi lubang dengan karangan. Katakan batas informasi dengan jelas."),
        ("cek konteks", "pastikan objek, jumlah, waktu, tempat, dan syarat sama dengan pertanyaan Admin."),
        ("cek premis", "periksa apakah pertanyaan mengandung premis salah, jebakan, atau syarat yang saling bertentangan."),
        ("jawaban pendek", "hindari paragraf panjang. Gunakan kalimat pendek dan poin seperlunya."),
        ("tidak lebay", "jangan memakai gaya promosi, klaim berlebihan, atau bahasa yang terlalu formal."),
        ("jelaskan alasan", "setiap kesimpulan penting harus punya alasan singkat yang bisa dicek."),
        ("validasi akhir", "sebelum jawaban akhir, cek apakah hasil memenuhi semua syarat yang diberikan."),
        ("data terbaru", "untuk data saat ini, pakai konteks web search bila tersedia dan jangan memakai ingatan lama yang bertentangan."),
        ("sumber dokumen", "jika Admin memberi dokumen/PDF, jawab berdasarkan dokumen dan jangan menambah informasi dari luar."),
        ("pilihan ganda", "baca stem dan semua opsi. Pilih opsi paling tepat, lalu jelaskan kenapa opsi lain kurang tepat."),
        ("soal hitungan", "tulis diketahui, ditanya, rumus, langkah singkat, cek ulang, dan jawaban akhir."),
        ("matematika rasio", "pisahkan rasio awal dan rasio akhir dengan variabel berbeda jika perlu, lalu validasi total/perubahan."),
        ("matematika aljabar", "jaga tanda, domain, pembagi nol, akar, dan substitusi balik ke persamaan awal."),
        ("matematika geometri", "identifikasi gambar/objek, satuan, teorema, dan apakah data cukup untuk menentukan jawaban."),
        ("fisika konsep", "bedakan besaran mirip seperti kecepatan/percepatan, massa/berat, energi/usaha/daya."),
        ("fisika satuan", "konversi ke SI dan cek dimensi jawaban sebelum menyimpulkan."),
        ("kimia stoikiometri", "setarakan reaksi, hitung mol, cek pereaksi pembatas, lalu kembalikan ke satuan yang diminta."),
        ("kimia larutan", "bedakan pH, pOH, konsentrasi, molaritas, pengenceran, dan kuat/lemah asam-basa."),
        ("english grammar", "cari subject, verb, modifier, tense, agreement, parallelism, dan pronoun reference."),
        ("toefl reading", "jawab berdasarkan evidence teks, bukan asumsi luar."),
        ("sejarah teliti", "jaga urutan waktu, tokoh, tempat, sebab, proses, dan dampak agar tidak tercampur."),
        ("pendidikan praktis", "bedakan tujuan, metode, media, asesmen, evaluasi, remedial, dan pengayaan."),
        ("coding siap jalan", "untuk aplikasi, jangan beri snippet kecil saja. Berikan struktur, kode, setup, cara run, dan test."),
        ("coding debugging", "baca error dari traceback, temukan akar masalah, beri patch minimal, dan cara verifikasi."),
        ("coding security", "cek validasi input, path traversal, overwrite, secret key, dan data sensitif."),
        ("coding arsitektur", "buat modul kecil, pisahkan UI, logic, database, konfigurasi, dan testing."),
        ("coding kualitas", "gunakan nama jelas, type hints bila membantu, error handling, logging, dan komentar seperlunya."),
        ("coding copyable", "kode wajib di fenced code block dengan info bahasa agar tombol Copy muncul."),
        ("ringkasan", "ambil ide pokok dan poin penting, bukan menyalin semuanya."),
        ("tugas menulis", "bantu susun draft yang rapi, tetapi jangan membuat klaim tanpa dasar."),
        ("jadwal belajar", "buat rencana realistis, pendek, bertahap, dan bisa langsung dijalankan."),
        ("teman diskusi", "tanggapi santai dan nyambung dengan konteks chat sebelumnya."),
        ("follow up", "jika Admin memakai 'itu', 'tadi', 'nya', atau 'lanjut', gunakan riwayat singkat sebagai konteks."),
        ("ganti topik", "jika Admin jelas mengganti topik, jangan terkunci pada topik lama."),
        ("jawaban sulit", "untuk soal sulit, pecah masalah menjadi bagian kecil dan cek setiap syarat."),
        ("anti kontradiksi", "jangan memberi dua kesimpulan yang saling bertentangan dalam satu jawaban."),
        ("minta detail", "jika pertanyaan ambigu, sebutkan asumsi atau minta detail tambahan secara singkat."),
        ("format nyaman", "pakai heading pendek atau poin ringan agar jawaban tidak bikin pusing."),
    ]

    notes = []
    for note in base_notes:
        for label, rule in hyper_rules:
            notes.append(
                {
                    "subject": note["subject"],
                    "trigger_text": f"{note['trigger_text']} {label}",
                    "correction": (
                        f"Hyper training untuk '{note['trigger_text']}': {rule} "
                        "Utamakan akurasi, konteks Admin, dan bahasa yang natural."
                    ),
                }
            )
    return notes


HYPER_TRAINING_NOTES = _build_hyper_training_notes(BULK_TRAINING_NOTES)

BRUTAL_TRAINING_NOTES.extend(
    {
        "subject": subject,
        "trigger_text": trigger_text,
        "correction": correction,
    }
    for subject, trigger_text, correction in ADVANCED_TRAINING_NOTES
)
BRUTAL_TRAINING_NOTES.extend(BULK_TRAINING_NOTES)
BRUTAL_TRAINING_NOTES.extend(MEGA_TRAINING_NOTES)
BRUTAL_TRAINING_NOTES.extend(ULTRA_TRAINING_NOTES)
BRUTAL_TRAINING_NOTES.extend(HYPER_TRAINING_NOTES)



def install_training_notes(notes: list[dict]) -> dict:
    init_db()
    with get_connection() as conn:
        existing_rows = conn.execute("SELECT subject, trigger_text, correction FROM learning_notes").fetchall()
    existing = {(row["subject"], row["trigger_text"], row["correction"]) for row in existing_rows}
    inserted = 0
    skipped = 0
    to_insert = []

    for note in notes:
        key = (note["subject"], note["trigger_text"], note["correction"])
        if key in existing:
            skipped += 1
            continue
        to_insert.append(key)
        existing.add(key)
        inserted += 1

    if to_insert:
        with get_connection() as conn:
            conn.executemany(
                """
                INSERT INTO learning_notes (subject, trigger_text, correction)
                VALUES (?, ?, ?)
                """,
                to_insert,
            )

    return {
        "inserted": inserted,
        "skipped": skipped,
        "total": len(notes),
    }


def install_brutal_training_pack() -> dict:
    return install_training_notes(BRUTAL_TRAINING_NOTES)
