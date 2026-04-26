# Referensi Desain - ORVIKO - Tiktok Slide

Dokumen ini merangkum referensi desain dari proyek ORVIKO - Main dan dijadikan acuan visual untuk ORVIKO - Tiktok Slide.

## Sumber referensi
- web/app/home/onboarding.css
- web/app/pricing/pricing.css
- web/app/login/login.css
- web/app/checkout/checkout.css
- web/app/payment/result.css
- web/app/legal/legal.css
- web/app/globals.css
- web/tailwind.config.ts
- extension/panel/src/panel/styles.css

## Arah visual
- Tampilan bersih dan premium dengan base putih dan gradasi pink lembut
- Aksen merah kuat untuk brand dan CTA
- Banyak kartu dengan radius besar dan shadow halus
- Kombinasi label uppercase dan teks body yang rapi

## Palet warna
### Brand dan aksen
- Red primary: #c1121f
- Red secondary: #e11d48
- Red deep: #b91c1c
- Blue accent: #2563eb
- Purple highlight: #7c3aed
- Orange highlight: #f97316

### Netral
- Text primary: #0f172a
- Text muted: #3f4857, #6b7280, #4b5563
- Surface: #ffffff
- Surface soft: #f8fafc, #f4f5f7
- Border: rgba(15,23,42,0.08), #e5e7eb
- Gray scale (Tailwind): #f4f5f7, #e5e7eb, #9ca3af, #6b7280, #3f4652, #1f232b

### Status
- Success: #15803d, #047857
- Warning: #b45309
- Error: #b91c1c

### Background gradient
- Radial: #fff1f2 -> #f8fafc -> #ffffff

## Tipografi
- Marketing pages: Space Grotesk (400-700)
- App dan extension: Inter
- Label uppercase dengan tracking 0.14em sampai 0.3em
- Headline memakai clamp size dan weight 700

## Layout dan grid
- Container max width 1200, center align
- Hero split grid (copy vs CTA card)
- Section grid 2-3 kolom, collapse ke 1 kolom pada 900-980px
- Workspace layout: header sticky + sidebar kiri sekitar 360px

## Komponen inti
- Brand mark bulat dengan border tipis dan logo berputar
- CTA button berbentuk pill dengan gradient merah
- Card panel: radius 18-22, 1px border, shadow lembut
- Badge/pill: uppercase, letter spacing besar, solid atau ghost
- Form input: radius 14, padding 12-14, border halus
- FAQ dan comparison cards berbasis grid
- Floating CTA di kanan bawah pada landing

## Motion
- Logo spin 8-10s linear infinite
- Hover lift pada CTA (translateY + shadow)
- Pulse loading pada placeholder di extension panel

## Responsif
- Breakpoint yang sering dipakai: 980px, 900px, 720px, 380px, 320px
- Grid dan nav stack saat mobile, tombol carousel disembunyikan

## Asset
- Onboarding media: web/public/onboarding/*
- Logo: web/public/logo.png

## Catatan konsistensi
- Ada dua bahasa visual: marketing (Space Grotesk + red gradient) vs app/extension (Inter + neutral gray). Jika ingin satu brand voice, samakan tipografi, warna aksen, dan style card di kedua area.
