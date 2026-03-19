# ODIN - TikTok Slide: Dokumentasi Fitur Lengkap

Dokumen ini menjelaskan fitur ODIN - TikTok Slide secara menyeluruh berdasarkan implementasi saat ini di frontend (`web/`) dan backend (`server/`).

## 1. Ringkasan Produk

ODIN - TikTok Slide adalah workspace untuk membuat gambar slide vertikal 9:16 (1080x1920) berbasis AI dengan konsep 3 panel:
- Panel kiri: manajemen slide dan input konten.
- Panel tengah: preview hasil slide aktif.
- Panel kanan: daftar hasil generasi untuk slide yang sedang dipreview.

Tujuan utama:
- Menulis teks slide.
- Menambahkan catatan desain opsional.
- Menyertakan gambar embed (logo/icon) sebagai referensi.
- Menghasilkan beberapa variasi gambar per slide.
- Memilih hasil terbaik lalu download.

## 2. Arsitektur dan Stack

### Frontend
- Next.js 14 (App Router), React 18, TypeScript.
- Lokasi: `web/`
- Halaman utama: `web/app/page.tsx`
- Styling utama: `web/app/globals.css`

### Backend
- FastAPI + SQLite.
- Lokasi: `server/`
- Entry app: `server/uvicorn_app.py`
- API utama: `server/app/main.py`
- Database helper: `server/app/core/db.py`
- Integrasi Gemini: `server/app/services/genai_client.py`

### Penyimpanan Lokal
- Root data: `data/` (dibuat otomatis).
- Embed image: `data/embeds/`
- Generated result image: `data/results/`
- SQLite DB: `data/tiktok_slide.db`

## 3. Fitur UI/UX Utama (Frontend)

## 3.1 Workspace 3 Kolom
- Header sticky dengan branding dan aksi download global.
- Grid 3 kolom desktop:
  - Kiri: input slide.
  - Tengah: preview canvas/image.
  - Kanan: generated results.
- Responsive:
  - <=1200px: panel kanan pindah ke bawah.
  - <=900px: layout jadi 1 kolom vertikal.

## 3.2 Resizable Left Panel
- Lebar panel kiri bisa di-resize drag pointer.
- Constraint lebar minimum/maksimum diterapkan agar panel tengah/kanan tetap usable.

## 3.3 Manajemen Slide
- Auto-load slide dari backend saat halaman dibuka.
- Jika belum ada slide: otomatis membuat `Slide 1`.
- Tambah slide baru via tombol `+ Add new slide`.
- Hapus slide dengan konfirmasi.
- Saat semua slide terhapus: sistem otomatis membuat slide baru agar workspace tidak kosong.

## 3.4 Dual Context: Active Slide vs Preview Slide
- `Active slide` (panel kiri): menentukan form input mana yang sedang diedit.
- `Preview slide` (panel tengah/kanan): menentukan slide mana yang sedang dilihat hasilnya.
- Keduanya sengaja dipisah:
  - Klik `Open/Active` mempengaruhi panel kiri saja.
  - Navigasi panah `<` `>` mempengaruhi panel tengah + kanan.

## 3.5 Input Konten Slide
- `Slide text` (wajib untuk generate).
- `User notes (optional)`:
  - Dipakai sebagai panduan style/konteks.
  - Tidak boleh muncul sebagai teks visual di gambar final.
- `Image quantity` 1-5 untuk jumlah hasil generasi per eksekusi.

Persistensi input:
- Saat `onBlur`, frontend mengirim PATCH ke backend agar perubahan tersimpan.

## 3.6 Embed Images (Logo/Icon)
- Upload multi-file image (`accept="image/*"`).
- Validasi frontend: hanya tipe image.
- Setiap embed punya:
  - Preview thumbnail.
  - Tombol delete.
  - Mode edit metadata (`Edit`):
    - `Label/Brand`
    - `Context`
- Label/context dipakai backend untuk membantu model menempatkan logo yang tepat sesuai konteks teks slide.

## 3.7 Generasi AI per Slide
- Tombol `Generate images` pada slide aktif.
- Frontend kirim request SSE ke endpoint generate.
- UI status:
  - Tombol berubah jadi `Generating...` saat proses berjalan.
  - Error generation ditampilkan inline pada slide aktif.
- Setelah proses selesai, frontend refresh data slide untuk memuat result terbaru.

## 3.8 Preview Behavior
- Jika slide punya result terpilih: panel tengah menampilkan image result.
- Jika belum ada image: panel tengah menampilkan placeholder preview berbasis teks slide:
  - Title/body/bullets (hasil parsing sederhana dari text).
  - Daftar chip logo dari embed labels.

## 3.9 Result Gallery dan Seleksi
- Panel kanan menampilkan semua result milik `preview slide`.
- Tiap card result menyediakan:
  - Thumbnail 9:16.
  - Title + note.
  - Tombol `Use for preview` (set selected result).
  - Tombol `Download`.
  - Tombol `Delete`.
- Badge `Selected` muncul pada result terpilih.

## 3.10 Download
- `Download selected`:
  - Download selected result untuk slide yang sedang dipreview.
- `Download image` (di preview panel):
  - Sama, download result terpilih.
- `Download slide pack`:
  - Download semua result slide yang sedang dipreview (satu per satu file).
- `Download all slides`:
  - Untuk tiap slide, ambil result terpilih, jika tidak ada ambil result pertama.
  - Download satu per satu file.

Catatan implementasi saat ini:
- Download dilakukan sebagai beberapa file individual, bukan ZIP.

## 3.11 Error & Empty State
- `loadError`: error load/save/upload/delete umum.
- `generationError`: error khusus generate.
- Empty state result: teks `No generated results yet.`
- Jika download diminta saat belum ada image/result: tampil error message.

## 4. Fitur API dan Backend

## 4.1 CORS & Startup
- DB di-init saat startup FastAPI.
- CORS origins diambil dari env `CORS_ALLOWED_ORIGINS`.

## 4.2 Endpoint Daftar Fitur
- `GET /health`
  - Health check backend.
- `GET /slides`
  - List semua slide + embeds + results.
- `POST /slides`
  - Buat slide baru.
- `GET /slides/{slide_id}`
  - Detail slide + embeds + results.
- `PATCH /slides/{slide_id}`
  - Update field slide.
- `DELETE /slides/{slide_id}`
  - Hapus slide + cleanup file embed/result di disk.
- `POST /slides/{slide_id}/embeds` (multipart)
  - Upload embed image ke slide.
- `PATCH /embeds/{embed_id}`
  - Update `label`/`context`.
- `DELETE /embeds/{embed_id}`
  - Hapus embed + file fisik.
- `GET /embeds/{embed_id}/file`
  - Ambil file embed untuk preview.
- `POST /slides/{slide_id}/generate` (SSE)
  - Generate result image untuk slide.
- `POST /slides/{slide_id}/results/{result_id}/select`
  - Set selected result pada slide.
- `GET /results/{result_id}/image`
  - Ambil image result untuk preview/download.
- `DELETE /results/{result_id}`
  - Hapus result + file fisik; jika result terpilih ikut direset.

## 4.3 Generate Flow (Backend)

Urutan proses di `/slides/{slide_id}/generate`:
1. Validasi slide exists.
2. Ambil embed metadata + bytes file embed.
3. Validasi `slide.text` tidak kosong.
4. Clamp quantity ke 1-5.
5. Bangun prompt dasar (slide text + notes + embed hints).
6. `refine_prompt()` ke model prompt.
7. Loop quantity:
   - `generate_images(...count=1)`.
   - Simpan image ke `data/results`.
   - Simpan record `slide_results`.
   - Jika belum ada selected result, auto-select result pertama.
   - Kirim SSE event `result` berisi ID + base64 image.
8. Kirim SSE `done`.

Jika gagal:
- SSE kirim event `error` dengan message.

## 4.4 Grounding (Google Search Tool)
- Request generate punya flag `grounding` (default `false`).
- Jika `grounding=true`:
  - Backend cek env `ALLOW_GOOGLE_SEARCH`.
  - Jika disabled, backend melempar error.
  - Jika enabled, config generate menyertakan tool `google_search`.

## 4.5 Prompt & Guardrails
- System prompt mengutamakan:
  - Format 9:16.
  - Teks slide harus digunakan penuh dan akurat.
  - User notes hanya guidance, bukan teks visual.
  - Komposisi aman terhadap overlay TikTok (margin atas/bawah).
  - Integrasi embed image secara kontekstual.
  - Hindari tambahan teks di luar slide text.

## 5. Data Model dan Database

## 5.1 Tabel `slides`
Kolom utama:
- `id`, `name`, `title`, `subtitle`
- `text`, `design`
- `quantity`, `position`
- `selected_result_id`
- `created_at`, `updated_at`

## 5.2 Tabel `slide_results`
Kolom utama:
- `id`, `slide_id`
- `title`, `note`, `tone`, `status`
- `image_path`
- `created_at`, `updated_at`

## 5.3 Tabel `embed_assets`
Kolom utama:
- `id`, `slide_id`
- `label`, `name`, `context`
- `file_path`, `mime_type`, `size`
- `created_at`

## 5.4 Aturan Integritas & File Lifecycle
- FK slide -> results/embeds dengan `ON DELETE CASCADE`.
- Saat slide dihapus:
  - Record DB dihapus.
  - File embed/result ikut dihapus dari disk.
- Saat embed/result dihapus:
  - File fisik ikut dihapus.
- Penghapusan file dibatasi agar tetap di dalam root `data/`.

## 6. Validasi dan Batasan

## 6.1 Validasi Schema (Pydantic)
- `quantity`: 1-5.
- `text` maks 5000 karakter.
- `design` maks 2000 karakter.
- `name`, `title`, `subtitle`, `label`, `context` punya limit panjang.

## 6.2 Validasi Runtime
- Generate ditolak bila `slide.text` kosong.
- Upload embed ditolak bila file kosong.
- Frontend menolak upload non-image via MIME check client-side.

## 6.3 Batasan Fungsional Saat Ini
- Belum ada autentikasi/otorisasi endpoint.
- Belum ada ZIP bundling bawaan untuk multi-download.
- Belum ada reorder drag-and-drop slide (position ada di data model, tapi UI reorder belum ada).
- Preview result tidak mengandalkan optimasi `next/image` (pakai `<img>` biasa).

## 7. Konfigurasi Environment

File `.env` di root proyek dipakai backend.

Variable utama:
- `GENAI_API_KEY`
- `GENAI_MODEL` (default: `gemini-3-flash-preview`)
- `IMAGE_AI_KEY`
- `IMAGE_GEN` (default: `gemini-3-pro-image-preview`)
- `IMAGE_ASPECT_RATIO` (default: `9:16`)
- `IMAGE_SIZE` (default: `2K`)
- `ALLOW_GOOGLE_SEARCH` (default: `false`)
- `SYSTEM_PROMPT` (opsional override)
- `CORS_ALLOWED_ORIGINS`

Frontend:
- `NEXT_PUBLIC_API_BASE_URL` (default fallback `http://127.0.0.1:8000`)

## 8. Alur Penggunaan End-to-End

1. User buka app, slide dimuat dari backend.
2. User isi `Slide text` dan optional `User notes`.
3. User upload embed image (opsional), edit label/context jika perlu.
4. User pilih jumlah output (1-5).
5. User klik `Generate images`.
6. Backend generate dan simpan result.
7. User pilih result via `Use for preview`.
8. User download result selected / semua result slide / semua slide.

## 9. Struktur Direktori yang Relevan

```text
ODIN - Tiktok Slide/
|- web/
|  |- app/
|  |  |- page.tsx
|  |  |- layout.tsx
|  |  |- globals.css
|  |- package.json
|- server/
|  |- app/
|  |  |- main.py
|  |  |- schemas.py
|  |  |- core/
|  |  |  |- config.py
|  |  |  |- db.py
|  |  |- services/
|  |     |- genai_client.py
|  |- pyproject.toml
|  |- uvicorn_app.py
|- data/               (auto-created)
|- README.md
|- app-flow.md
```

## 10. Checklist Fitur (Quick Audit)

- [x] 3-panel workspace UI.
- [x] Auto-create first slide.
- [x] Add/delete slide.
- [x] Edit slide text/notes/quantity.
- [x] Upload multiple embed images.
- [x] Edit embed label + context.
- [x] Delete embed image.
- [x] Generate AI image (SSE flow).
- [x] Persist result ke DB + file system.
- [x] Select result untuk preview.
- [x] Delete result.
- [x] Download selected result.
- [x] Download semua result dalam satu slide (multi file).
- [x] Download semua slide (multi file).
- [x] Responsive layout.
- [x] CORS configurable.

## 11. Catatan Teknis Penting

- Konfigurasi `web/next.config.mjs` memakai `output: 'export'`, tetapi app juga bergantung pada API runtime backend; jadi mode penggunaan normal tetap sebagai web app dinamis yang memanggil API backend.
- Event SSE `result` mengirim `image_base64`, namun frontend saat ini mengandalkan refresh data slide dan mengambil image via endpoint file, bukan merender base64 streaming langsung.
- Field `allow_unauthenticated_generate` tersedia di config backend tetapi belum digunakan untuk kontrol akses endpoint generate.

## 12. Rekomendasi Peningkatan (Opsional)

1. Tambahkan endpoint ZIP untuk `download selected` multi-slide dan `download all`.
2. Tambahkan auth minimal (token/session) untuk proteksi endpoint delete/generate.
3. Tambahkan reorder slide di UI untuk memanfaatkan `position`.
4. Tampilkan progress SSE per item (mis. `Generating option 2/5`).
5. Tambahkan unit/integration test untuk alur DB cleanup file.

