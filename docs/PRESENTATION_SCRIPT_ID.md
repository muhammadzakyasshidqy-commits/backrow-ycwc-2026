# BACKROW 11.0 — Naskah Presentasi Internasional (Bahasa Indonesia)

> Gunakan versi Inggris untuk International Final jika aturan mewajibkan bahasa Inggris. Dokumen ini untuk latihan, tahap Indonesia, dan memastikan argumen dipahami tanpa jargon.

## Slide 1 — Informasinya berubah

“Slide ini menulis 2,5 persen. Tetapi dari posisi penonton, informasi yang tertangkap berubah menjadi 25 persen. Penonton tidak pernah melihat file sumber. Mereka melihat hasil akhir setelah jarak, proyeksi, fokus, pencahayaan, dan perspektif. BACKROW menguji jalur fisik itu.”

## Slide 2 — Masalah yang tepat

“Presenter biasanya menilai slide dari laptop sendiri atau berjalan ke belakang ruangan dan memeriksanya manual. Tool yang hanya melihat file sumber bisa mengecek ukuran font, kontras, atau kompleksitas teks, tetapi tidak bisa membuktikan apa yang benar-benar sampai dari ruangan dan posisi penonton tertentu.”

## Slide 3 — Apa yang dilakukan BACKROW

“Saya memuat deck sekali, lalu menaruh kamera di posisi penonton. Ketika presentasi berjalan, BACKROW mengenali slide aktif, meluruskan pandangan kamera, memetakan bukti kembali ke slide sumber, lalu menunjukkan informasi mana yang pulih, meragukan, atau hilang.”

## Slide 4 — Bukti langsung

“Silakan pilih satu slide. Saya tidak akan memberi nomor halamannya kepada BACKROW. Sistem harus mengenali slide itu sendiri. Pada contoh ini sumber berisi 2,5 persen, tetapi bukti dari posisi penonton terbaca 25 persen, sehingga region itu ditandai berisiko.”

## Slide 5 — Mana yang benar-benar AI

“Model kustom kami adalah AudienceNet 2.0, neural network kecil yang memakai pasangan fitur dari sumber, kamera, dan opsional kondisi ruangan. Tesseract LSTM adalah OCR pretrained pihak ketiga. ORB, RANSAC, homography, ekstraksi angka, dan fusi bukti adalah engineering klasik. Kami memisahkan semuanya dan tidak menyebut seluruh pipeline sebagai AI.”

## Slide 6 — Hierarki keselamatan

“Model learned tidak boleh mengalahkan bukti keras. Jika sumber mengatakan 2,5 persen dan OCR kamera yang kuat mengatakan 25 persen, kontradiksi itu yang menang. Jika slide tidak bisa dicocokkan atau buktinya terlalu lemah, BACKROW menolak memberi kesimpulan.”

## Slide 7 — Prior art dan novelty

“Software keterbacaan ruang kuliah sudah ada sejak lama. Penilaian kualitas proyeksi berbasis kamera juga sudah pernah diteliti, dan tool modern dapat memeriksa file PowerPoint sumber. Jadi saya tidak mengklaim readability sebagai hal baru. Kontribusi BACKROW adalah workflow terintegrasi dari posisi penonton: pencocokan slide otomatis, bukti fisik, kehilangan informasi yang terlokalisasi, perbaikan, scan ulang, dan validasi fisik blind.”

## Slide 8 — Bukti engineering

“Pada curriculum procedural, AudienceNet 2.0 mencapai macro-F1 0,9422, dibanding 0,4056 dan 0,4789 untuk dua baseline sederhana. Bundled deck tiga halaman berhasil dicocokkan 3 dari 3 tanpa nomor halaman. Regression test mendeteksi kegagalan 2,5 menjadi 25 persen, dan versi yang diperbaiki menghapus dua region risiko. Ini hasil engineering, bukan akurasi manusia.”

## Slide 9 — Tes manusia

“Kamera bukan mata manusia. Karena itu pengujian akhir memakai pembaca naïve, urutan acak yang dibekukan, paparan enam detik secara default, sumber asli disembunyikan, respons tidak bisa diedit setelah dikirim, calibration dipisahkan dari locked test, dan evaluator memakai confidence interval serta kill gate yang sudah ditentukan.”

## Slide 10 — Temukan, perbaiki, buktikan

“Produk ini bukan sekadar skor. Loop-nya adalah: temukan informasi yang hilang, perbaiki region sumber, lalu scan ulang dari posisi penonton yang sama. BACKROW hanya bernilai jika loop itu benar-benar meningkatkan informasi yang bisa dipulihkan penonton. Silakan pilih satu slide.”
