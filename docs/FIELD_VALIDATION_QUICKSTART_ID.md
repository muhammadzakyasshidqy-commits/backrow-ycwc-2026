# BACKROW 11.0 — Quickstart Validasi Fisik

Setelah BACKROW dijalankan dengan field-study launcher, buka `/validate.html?lang=id`.

## A. Manual vs BACKROW

Gunakan deck rehearsal yang sama dan sudah dibekukan, minimal 15 slide.

1. Isi jumlah slide dan total kegagalan kritis yang diketahui.
2. Mulai timer **Manual**. Lakukan workflow manual penuh dan catat berapa kegagalan yang ditemukan.
3. Mulai timer **BACKROW** dengan deck dan kondisi yang sama.
4. Ekspor `BACKROW_WORKFLOW.json`.

Jangan mengedit deck di tengah locked comparison.

## B. Pencocokan deck pada proyektor nyata

1. Unggah PDF yang tepat sekali.
2. Pilih nomor slide yang benar sebelum mengambil frame.
3. Buka kamera dari posisi penonton.
4. Ambil frame stabil dari beberapa slide dan posisi/kondisi berbeda.
5. BACKROW mencatat halaman hasil match, rejection, inliers, inlier ratio, coverage, dan latency.
6. Ekspor `BACKROW_DECK_MATCH.json`.

Frame ambigu yang ditolak tetap dihitung sebagai rejection. Jangan dihapus atau dilabel ulang.

## C. Locked human evaluation

Buat field study dari hasil BACKROW, lalu gunakan presenter console dan reader form. Reader tidak boleh melihat source truth atau prediksi BACKROW sebelum mengirim jawaban.

Gabungkan hasil locked reader study dengan kedua ekspor di atas melalui:

`python training/evaluate_locked_field_studies.py LOCKED_STUDY.json --workflow-json BACKROW_WORKFLOW.json --deck-json BACKROW_DECK_MATCH.json --out docs/FIELD_LOCKED_TEST_REPORT.json`
