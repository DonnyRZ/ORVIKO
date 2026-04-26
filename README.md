# ORVIKO

ORVIKO adalah workspace kreator untuk dua kebutuhan utama:

- membantu kreator menyusun draft script yang tetap terasa seperti gaya kontennya sendiri
- membantu kreator membuat visual postingan lebih cepat dari teks sederhana

Project ini terdiri dari frontend Next.js dan backend FastAPI dengan SQLite lokal.

## Scope Produk Saat Ini

ORVIKO saat ini sudah mencakup:

- landing page public di `/`
- checkout flow V1 di `/checkout`
- contact page di `/contact`
- terms page di `/terms`
- payment dummy page di `/payment`
- dashboard internal di `/home`
- workspace script di `/script`
- workspace postingan gambar di `/slides`
- histori project di `/history`

## Value Utama

### 1. Script yang lebih personal

ORVIKO membaca pola dari script referensi yang di-upload, lalu membantu membangun:

- source shortlist
- observasi: perilaku, emosi, situasi
- momen

arahnya adalah membantu kreator sampai ke draft script yang tetap terasa dekat dengan persona dan ritme kontennya.

### 2. Visual postingan yang lebih cepat

ORVIKO juga punya workspace visual untuk:

- menulis teks slide
- menambahkan notes opsional
- upload embed image seperti logo atau icon
- memilih aspect ratio
- generate beberapa variasi visual

## Arsitektur Singkat

### Frontend

- Next.js 14
- React 18
- TypeScript
- App Router
- `output: 'export'` untuk build static

### Backend

- FastAPI
- SQLite
- Google GenAI integration
- local file storage untuk embed image dan generated results

## Struktur Project

```txt
web/
  app/
    page.tsx          # landing page
    checkout/         # checkout page
    contact/          # contact page
    history/          # history page
    home/             # dashboard internal
    payment/          # payment dummy page
    script/           # script workspace
    slides/           # image workspace
    terms/            # terms page
  features/
    landing/
    checkout/
    home/
    payment/
    script/
    slides/
    contact/
    legal/

server/
  app/
    core/             # config, db
    prompting/        # prompting runtime
    routes/           # auth, script, slides
    schemas/          # pydantic schemas
    services/         # genai client, script service
  tests/
```

## Route Frontend

- `/` -> landing page
- `/checkout` -> pilih paket
- `/contact` -> halaman contact
- `/terms` -> halaman terms
- `/payment` -> payment dummy
- `/home` -> dashboard internal
- `/script` -> workspace script
- `/slides` -> workspace postingan gambar
- `/history` -> histori project

## Route Backend Utama

### Health

- `GET /health`

### Slides

- `GET /slides`
- `GET /slides/history`
- `GET /slides/gallery`
- `POST /slides`
- `POST /slides/workspace/reset`
- `GET /slides/{slide_id}`
- `PATCH /slides/{slide_id}`
- `DELETE /slides/{slide_id}`
- `POST /slides/{slide_id}/embeds`
- `POST /slides/{slide_id}/generate`

### Script

- `GET /script/workspace`
- `POST /script/workspaces`
- `GET /script/workspaces/{workspace_id}`
- `GET /script/history`
- `PATCH /script/workspace/task`
- `POST /script/workspace/source-options`
- `PATCH /script/workspace/source`
- `POST /script/workspace/observations/generate`
- `PATCH /script/workspace/observations`
- `POST /script/workspace/moments/generate`
- `PATCH /script/workspace/moments`

Script route juga punya varian berbasis `workspace_id`.

### Auth

- `GET /auth/google/login`
- `GET /auth/google/callback`

## Persiapan Lokal

### Prasyarat

- Node.js 22 disarankan
- npm
- Python 3.10+

## Environment Variables

Backend membaca `.env` di root repo.

Contoh minimal:

```env
GENAI_API_KEY=your_text_model_key
GENAI_MODEL=gemini-3-flash-preview

IMAGE_AI_KEY=your_image_model_key
IMAGE_GEN=gemini-3-pro-image-preview

IMAGE_ASPECT_RATIO=9:16
IMAGE_SIZE=2K
ALLOW_GOOGLE_SEARCH=false

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOW_UNAUTHENTICATED_GENERATE=true

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
FRONTEND_BASE_URL=http://localhost:3000
```

Frontend bisa memakai `web/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Catatan penting:

- `NEXT_PUBLIC_API_BASE_URL` dibaca saat build frontend
- karena frontend memakai static export, value ini bukan runtime env browser biasa

## Menjalankan Secara Lokal

### 1. Backend

Dari root repo:

```powershell
cd server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
uvicorn uvicorn_app:app --reload
```

Backend default:

- `http://127.0.0.1:8000`
- docs: `http://127.0.0.1:8000/docs`

### 2. Frontend

Dari root repo:

```powershell
cd web
npm install
npm run dev
```

Frontend default:

- `http://localhost:3000`

## Flow Penggunaan Singkat

### Script workspace

1. buka `/script`
2. isi task atau query
3. generate source shortlist
4. pilih atau edit source
5. generate observasi
6. generate momen
7. edit hasil jika perlu

### Slide workspace

1. buka `/slides`
2. isi judul dan teks slide
3. tambah notes bila perlu
4. upload embed image bila perlu
5. pilih aspect ratio
6. generate result
7. pilih preview dan download

## Production Notes

### Frontend adalah static export

`web/next.config.mjs` memakai:

- `output: 'export'`
- `trailingSlash: true`

Artinya:

- `npm run build` menghasilkan output static di `web/out`
- untuk production, frontend sebaiknya diserve oleh Nginx atau static file server
- `next start` tidak cocok untuk production build project ini

### Backend production

Backend sebaiknya dijalankan sebagai service, misalnya `systemd`, bukan terminal manual.

Contoh pendek:

- service backend FastAPI / uvicorn
- Nginx untuk:
  - serve `web/out`
  - proxy route backend yang diperlukan
- SSL via Certbot

## Status Flow Bisnis Saat Ini

Flow bisnis yang ada sekarang masih V1:

- landing page
- checkout
- login Google
- payment dummy

Catatan:

- payment page belum terhubung ke payment gateway asli
- autentikasi saat ini belum final
- proteksi workspace internal belum dianggap production-ready

Jadi branch ini cocok untuk:

- review flow
- review UX
- review integrasi awal

Belum cocok untuk public launch tanpa hardening tambahan.

## File Referensi Produk

Beberapa dokumen penting di repo:

- `AI_PROMPTING_FRAMEWORK.md`
- `source-situasi.md`
- `momen.md`
- `knowledge-base.md`
- `app-flow.md`
- `Script Planning.txt`

## Catatan Tambahan

- data SQLite dan file hasil generate disimpan lokal oleh backend
- histori slide dan script sekarang berbasis project id, bukan singleton overwrite lama
- landing page sudah memakai brand ORVIKO
- build frontend bisa gagal bila ada route client-only yang belum dibungkus `Suspense`

## License

Belum ditetapkan.
