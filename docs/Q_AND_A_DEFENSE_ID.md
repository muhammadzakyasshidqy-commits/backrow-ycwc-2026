# BACKROW 11.0 — Pertahanan Q&A Bahasa Indonesia

Semua jawaban harus tetap berada di dalam bukti yang benar-benar diukur.

## “Kenapa tidak jalan saja ke belakang?”

Untuk satu slide, itu masuk akal. BACKROW menargetkan rehearsal seluruh deck: deck dimuat sekali, kamera ditinggal di posisi penonton, presenter maju seperti biasa, lalu sistem memberi bukti yang dipetakan kembali ke region sumber dan bisa di-rescan. Perbandingan waktu dan kegagalan kritis terhadap pemeriksaan manual diukur di Physical Validation Console.

## “Kenapa tidak perbesar semua font?”

Karena ukuran font sumber hanya satu variabel. Proyeksi nyata bisa kehilangan informasi karena jarak, fokus, washout, silau, kontras, perspektif, dan kondisi display/capture. BACKROW juga menyimpan baseline geometri sumber supaya kelemahan source-side bisa dibedakan dari kegagalan yang ditambahkan ruangan/display.

## “Bukankah software lecture-hall legibility sudah ada?”

Ya. Cai, Kim & Green menerbitkan program keterbacaan teks ruang kuliah pada 2011. Itu prior art yang diakui. Kontribusi BACKROW lebih sempit: workflow kamera penonton dengan pencocokan slide otomatis, bukti kehilangan informasi yang terlokalisasi, repair/rescan, dan validasi fisik terkunci.

## “Bagaimana dengan riset projector-camera?”

Le dkk. pada CRV 2017 sudah memakai tangkapan kamera dari proyeksi untuk penilaian kualitas visual dan menyebut gap kamera-vs-viewer. BACKROW tidak mengklaim menemukan bidang itu. BACKROW membangun workflow presenter yang berbeda dan mengukur gap kamera/manusia melalui field study, bukan menyamakan kamera dengan mata manusia.

## “Kenapa bukan PowerPoint Accessibility Checker / SlideSpeak?”

Tool itu berguna untuk pemeriksaan file sumber. BACKROW menjawab pertanyaan berbeda: informasi apa yang benar-benar bertahan setelah jalur ruangan/display/kamera nyata? Bukti fisik itu dipetakan kembali ke region sumber, lalu presenter bisa memperbaiki dan scan ulang.

## “Kenapa bukan ChatGPT?”

Model multimodal frontier memang dapat membandingkan satu slide sumber dan satu gambar audience. BACKROW tidak menyangkal itu. Kelebihan struktural BACKROW adalah akuisisi whole-deck otomatis, pencarian halaman sumber, correspondence geometrik, pemeriksaan nilai exact yang deterministik, hierarki bukti yang repeatable, fail-closed state, dan fix/rescan. Klaim superiority terhadap frontier AI hanya boleh dibuat setelah locked same-evidence baseline benar-benar selesai.

## “Bagian mana yang AI?”

Dua komponen AI:

1. **AudienceNet 2.0** — model kustom 48→24 MLP dengan 16 fitur pasangan source/camera/room.
2. **Tesseract 5 LSTM OCR** — AI pretrained pihak ketiga untuk pemulihan teks exact.

ORB, RANSAC/homography, ekstraksi angka, geometri sumber, dan evidence fusion adalah komponen klasik/deterministik dan tidak diklaim sebagai AI.

## “Apa yang kalian latih?”

AudienceNet 2.0. Model bundled dilatih pada 1.440 contoh procedural seimbang dari 48 family template teks, dengan split family yang group-disjoint. Test macro-F1-nya 0,9422 dibanding 0,4056/0,4789 untuk dua baseline sederhana bundled. Angka itu adalah metrik procedural, bukan akurasi keterbacaan manusia.

## “Kalau sudah ada OCR, buat apa AudienceNet?”

OCR memberikan bukti konten langsung ketika teks berhasil didecode dengan confidence kuat. AudienceNet memberi learned survivability evidence pada kondisi visual ambigu. Ablation harus membuktikan learned channel benar-benar menambah keputusan pada kasus seperti itu. Namun bukti exact OCR/angka selalu lebih tinggi prioritasnya daripada AudienceNet.

## “Kamera bukan mata manusia. Berarti idenya invalid dong?”

Kamera memang bukan mata manusia. Itu batas desain utama. Kamera memberikan bukti fisik yang bisa diukur; blind human field study mengukur hubungan antara bukti itu dan kemampuan pembaca naïve memulihkan informasi. Karena itu BACKROW tidak boleh mengklaim probabilitas manusia sebelum real-field calibrator benar-benar dilatih dan lolos locked test.

## “Berapa orang yang diuji?”

Sebutkan hanya jumlah aktual dari hasil locked field evaluation. Jangan mengarang angka. Jika belum selesai, tampilkan collector blind, protokol, dan status bahwa klaim human-calibrated belum dibuka.

## “Apakah test slide pernah masuk training?”

Split procedural AudienceNet group-disjoint berdasarkan family template. Untuk calibration manusia, development study dan locked study memakai study ID berbeda dan evaluator menolak leakage. Pelaporan fisik juga harus memisahkan kondisi room/slide/device.

## “Kalau kamera blur atau slide salah?”

BACKROW boleh abstain. Identitas deck ambigu, geometri gagal, kualitas capture terlalu buruk, atau bukti tidak cukup harus menghasilkan rejection/unknown, bukan jawaban palsu.

## “Kenapa website?”

Browser secara natural mendukung PDF/file input, kamera, perangkat peserta kedua, LAN study collection, cross-platform exhibition, dan demo tanpa instalasi khusus. Website adalah bagian workflow, bukan pembungkus chat prompt.

## “Kalau internet mati?”

Core analysis berjalan pada instance BACKROW dengan dependency lokal/bundled dan tanpa third-party AI API. Perangkat exhibition tetap harus dipreflight. Bundled deterministic demo adalah fallback jika live capture gagal karena kondisi venue.

## “Bisa saya coba slide saya sendiri?”

Bisa. Pilih Cek slide sungguhan, muat source/PDF yang tepat, ambil kamera/foto dari posisi penonton, lalu biarkan BACKROW mencocokkan dan menganalisis. Input ambigu harus fail-closed dan tidak boleh mewarisi hasil demo.

## Kenapa tidak jalan saja ke baris belakang?
Itu tetap baseline manual paling sederhana dan memang harus dibandingkan. Workflow dua-perangkat saat ini menghilangkan friction terbesar: laptop presenter tetap di depan, sementara satu HP yang sudah dipasangkan tetap berada di posisi penonton. Di HTTPS HP dapat menjalankan scan live; pada HTTP lokal masih ada fallback ambil foto. Bukti hasil matching dan analisis masuk kembali ke workstation presenter secara otomatis. Jadi perbandingannya bukan “AI lawan mata”, tetapi bolak-balik manual + ingatan manusia dibanding satu sudut penonton yang terus terukur.

## HP kedua cuma alat demo palsu?
Tidak. Halaman observer adalah web client sungguhan dengan token sesi sendiri. Pairing memakai kode enam digit, kamera/foto menangkap layar proyektor nyata, server melakukan matching slide tanpa diberi nomor halaman lalu menjalankan pipeline BACKROW. Source answer tidak ditampilkan di halaman observer.
