import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")


def get_site_data():
    return {
        "name"        : "BelajDeutsch",
        "tagline"     : "Platform Simulasi Ujian Bahasa Jerman Terpercaya & AI Feedback",
        "description" : "Persiapkan ujian Goethe-Zertifikat (A1–C2), TestDaF, dan DSH kamu dengan simulasi terstandar, feedback analisis AI cerdas, dan pembahasan mendalam.",
        "contact_email": "hello@belajdeutsch.id",
        "contact_wa"  : "https://api.whatsapp.com/send?phone=628123456789",
        "features": [
            {
                "icon" : "📝",
                "title": "Standar Ujian Resmi",
                "desc" : "Disusun mengikuti format resmi Goethe-Institut (A1–C2), TestDaF, dan DSH."
            },
            {
                "icon" : "🤖",
                "title": "Evaluasi & Feedback AI",
                "desc" : "Dapatkan analisis otomatis dari AI mengenai kelebihan, kekurangan, dan estimasi level CEFR setelah tes."
            },
            {
                "icon" : "⏱️",
                "title": "Simulasi Waktu Nyata",
                "desc" : "Timer per seksi yang akurat: Hören, Lesen, Schreiben, Sprechen persis seperti ujian sebenarnya."
            },
            {
                "icon" : "📊",
                "title": "Analisis Skor Akurat",
                "desc" : "Dapatkan skor per seksi dan level kompetensi langsung setelah ujian selesai."
            },
            {
                "icon" : "💡",
                "title": "Pembahasan Detail",
                "desc" : "Akses pembahasan lengkap tata bahasa (Grammatik), kosakata (Wortschatz), dan strategi pengerjaan soal."
            },
            {
                "icon" : "💾",
                "title": "Auto-Save Jawaban",
                "desc" : "Jawaban tersimpan otomatis setiap saat. Koneksi terputus? Lanjut dari titik yang sama."
            },
        ],
        "test_types": [
            {
                "code" : "A1-A2",
                "title": "Goethe-Zertifikat A1 – A2",
                "desc" : "Tingkat Dasar (Elementare Sprachverwendung): Hören, Lesen, Schreiben",
                "sections": ["Hören (20-30 mnt)", "Lesen (25-30 mnt)", "Schreiben (20-30 mnt)"],
                "color": "emerald",
            },
            {
                "code" : "B1-B2",
                "title": "Goethe-Zertifikat B1 – B2",
                "desc" : "Tingkat Menengah (Selbstständige Sprachverwendung): untuk kuliah / kerja",
                "sections": ["Hören (40 mnt)", "Lesen (65 mnt)", "Schreiben (60-75 mnt)", "Sprechen (15 mnt)"],
                "color": "blue",
            },
            {
                "code" : "TESTDAF",
                "title": "TestDaF & DSH",
                "desc" : "Persiapan studi perguruan tinggi di Jerman (Hochschulzugang)",
                "sections": ["Leseverstehen", "Hörverstehen", "Schriftlicher Ausdruck", "Mündlicher Ausdruck"],
                "color": "purple",
            },
        ],
        "faqs": [
            {
                "q": "Apa perbedaan paket Basic dan Premium?",
                "a": "Semua paket berbayar membuka seluruh simulasi ujian. Yang berbeda adalah jumlah Kredit AI untuk feedback analisis: Basic 150 kredit/bulan, Pro 400, Premium 900 — plus rekomendasi belajar personal dan pembahasan lengkap.",
            },
            {
                "q": "Bagaimana AI memberikan feedback setelah tes?",
                "a": "Sistem AI terintegrasi langsung mengevaluasi pola jawaban kamu, mendeteksi kelemahan tata bahasa / kosakata, dan memberikan rekomendasi latihan terarah.",
            },
            {
                "q": "Bagaimana cara pembayaran?",
                "a": "Pilih paket dan durasi (bulanan, 3 bulan, atau tahunan), lalu bayar via transfer bank/e-wallet. Setelah konfirmasi admin (maks. 1×24 jam), seluruh ujian langsung terbuka.",
            },
            {
                "q": "Apakah soal bisa diacak?",
                "a": "Ya. Sistem mengacak urutan konteks soal (passage-aware), namun soal-soal dalam satu teks bacaan/audio tetap dalam satu kesatuan.",
            },
            {
                "q": "Berapa lama akses berlaku?",
                "a": "Akses mengikuti durasi langgananmu — 1, 3, atau 12 bulan. Berlangganan lagi masa aktif akan ditumpuk (tidak hangus).",
            },
        ],
    }
# end def
