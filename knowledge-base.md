# Knowledge Base

Dokumen ini merekap pendekatan yang benar untuk `knowledge base` dalam flow pembuatan ide konten.

Dokumen ini dibuat sebagai pasangan dari:

- [source-situasi.md](c:/Project/ODIN-Tiktok/source-situasi.md)
- [momen.md](c:/Project/ODIN-Tiktok/momen.md)

Kalau `source-situasi.md` menjelaskan fondasi observasi manusia, dan `momen.md` menjelaskan bagaimana observasi itu berubah menjadi rangkaian scene, maka dokumen ini menjelaskan fondasi yang membuat semua itu bisa selaras dengan gaya kreator.

---

## Tujuan Utama

Knowledge base dipakai agar sistem tidak menghasilkan output yang technically benar tetapi terasa asing bagi kreator.

Tanpa knowledge base, AI mungkin masih bisa:

- menemukan source yang cukup bagus
- menghasilkan perilaku, emosi, dan situasi yang cukup relatable
- menyusun momen yang cukup runtut

Tetapi semua itu masih berisiko terasa:

- terlalu generik
- tidak khas
- tidak seperti cara kreator biasanya membuat konten
- tidak cocok dengan ritme, sudut pandang, dan kebiasaan storytelling kreator

Jadi tujuan knowledge base adalah:

- membuat sistem memahami pola kreator
- membuat output tidak sekadar “masuk akal”, tapi juga “terasa milik kreator”
- menjadi lapisan kecerdasan yang dipakai saat generate, bukan sekadar arsip dokumen

---

## Apa itu Knowledge Base dalam Sistem Ini

Dalam konteks flow ini, `knowledge base` bukan berarti kumpulan PDF, kumpulan script mentah, atau vector database raw retrieval yang dibaca ulang setiap kali query.

Knowledge base yang dimaksud di sini adalah:

> hasil distilasi dari script-script terdahulu milik kreator menjadi struktur pengetahuan yang menangkap pola, kecenderungan, dan ciri khas cara kreator berpikir serta membangun konten

Jadi knowledge base bukan:

- dokumen mentah
- kumpulan ringkasan acak
- catatan panjang yang tidak terstruktur

Knowledge base harus menjadi sesuatu yang:

- sudah dipahami dulu oleh sistem
- sudah disaring
- sudah ditata
- siap dipakai saat runtime

---

## Kenapa Raw Script Tidak Cukup

Kalau sistem hanya menyimpan raw scripts, ada beberapa masalah:

1. **Terlalu mahal dibaca berulang**
   Sistem akan cenderung membaca terlalu banyak bahan untuk pertanyaan yang seharusnya bisa dijawab dengan pola yang sudah disimpulkan sebelumnya.

2. **Terlalu berisik**
   Script mentah berisi banyak detail yang tidak semuanya penting untuk generation.

3. **Tidak langsung menangkap pola**
   Yang kita butuhkan bukan sekadar kalimat-kalimat lama, tetapi:
   - pola source yang sering dipakai
   - pola perilaku yang sering diangkat
   - emosi yang khas
   - bentuk situasi yang sering muncul
   - ritme momen yang menjadi ciri kreator

4. **Momen paling rawan meleset tanpa distilasi**
   Seperti yang sudah kita pahami, source sampai situasi mungkin masih bisa lumayan tanpa alignment yang dalam. Tetapi begitu masuk ke momen, sistem harus mulai menyusun scene. Di titik ini, kalau style kreator tidak benar-benar dipahami, hasilnya akan terasa jauh dari kebiasaan kreator.

Jadi raw scripts tetap penting, tetapi perannya adalah:

- **input untuk membangun knowledge base**

Bukan:

- **source of truth utama yang dibaca mentah terus-menerus saat generate**

---

## Peran Knowledge Base di Tiap Tahap

### 1. Saat memilih source

Knowledge base membantu sistem menjawab:

- source seperti apa yang paling sering dipakai kreator?
- sumber ketegangan apa yang paling cocok untuk audiens kreator?
- kreator ini cenderung bermain di keresahan, desire, fear, behavior, atau trend seperti apa?

Knowledge base di tahap ini bukan dipakai untuk menghasilkan satu jawaban final secara diam-diam, tetapi untuk membantu sistem membuat shortlist source yang paling relevan bagi user.

---

## Metode Pemilihan Source yang Memakai Knowledge Base

Best practice untuk pemilihan source dalam sistem ini adalah:

1. user memberi task atau query
2. sistem membaca knowledge base
3. sistem mencari source yang paling relevan berdasarkan:
   - tujuan query user
   - audience profile kreator
   - source library yang paling sering cocok
   - pola framing kreator
4. sistem menyusun shortlist beberapa source yang paling layak
5. agent menampilkan opsi itu ke user
6. user memilih salah satu, atau memasukkan source versi sendiri lewat free text

Jadi knowledge base berperan sebagai:

- filter
- pemberi konteks
- pemberi prioritas

Bukan sebagai:

- pengganti keputusan user sepenuhnya

### Kenapa perlu shortlist, bukan satu source final langsung

Karena satu query yang sama sering bisa dibuka dari beberapa source berbeda.

Contoh:

Kalau user ingin bahas kreator yang views-nya seret, sistem bisa membuka arah dari:

- frustration
- fear
- desire
- behavior

Semua bisa benar, tetapi tidak semua pasti sesuai dengan niat user saat itu.

Karena itu, runtime yang sehat adalah:

- knowledge base mempersempit kemungkinan
- user tetap memilih arah akhir

### Apa yang seharusnya di-ranking oleh sistem

Saat membuat shortlist source, sistem sebaiknya memikirkan beberapa hal berikut:

- seberapa dekat source itu dengan query user
- seberapa sering source seperti itu muncul dalam pola kreator
- seberapa cocok source itu dengan audience kreator
- seberapa kuat source itu untuk diturunkan ke perilaku, emosi, dan situasi

Jadi source tidak dipilih hanya karena sering dipakai duluan, tetapi karena:

- relevan
- cocok
- dan bisa berkembang

### Output pemilihan source yang ideal

Output agent pada tahap ini sebaiknya bukan hanya menyebut kategori besar.

Yang paling ideal adalah agent menampilkan beberapa opsi source yang sudah:

- spesifik
- contextual
- mudah dipilih user

Contoh:

- `Frustration: merasa kontennya sudah niat, tapi hasilnya kalah sama konten yang lebih ringan`
- `Desire: ingin terlihat semakin paham soal konten di depan orang lain`
- `Fear: takut dianggap tidak berkembang walaupun sudah konsisten upload`

Dengan bentuk seperti ini, user tidak perlu menebak-nebak arti source.

---

### 2. Saat menghasilkan perilaku, emosi, dan situasi

Knowledge base membantu sistem menjawab:

- observasi seperti apa yang biasanya dipakai kreator?
- cara melihat manusia seperti apa yang paling khas?
- emosi macam apa yang sering dimunculkan?
- situasi seperti apa yang terasa dekat dengan dunia kontennya?

### 3. Saat menyusun momen

Ini titik terpenting.

Knowledge base membantu sistem menjawab:

- scene seperti apa yang cocok dengan style kreator?
- bagaimana cara kreator biasanya membuka konten?
- bagaimana dia membangun tensi?
- jenis benturan seperti apa yang sering dipakai?
- ritme scene-nya cepat atau lambat?
- penutupnya biasanya menampar, reflektif, satir, atau observasional?

Tanpa knowledge base yang kuat, tahap momen paling mudah terasa salah.

---

## Bentuk Knowledge Base yang Benar

Knowledge base dalam sistem ini sebaiknya dipahami sebagai:

`creator intelligence layer`

Artinya, isi knowledge base harus berupa pola yang bisa dipakai agent, bukan sekadar tulisan yang enak dibaca manusia.

### Karakter knowledge base yang baik

- terstruktur
- ringkas tapi kaya makna
- bisa dipecah per bagian
- bisa dipakai ulang
- bisa di-update sebagian tanpa harus menulis ulang semuanya

### Karakter knowledge base yang lemah

- hanya berupa summary panjang
- campur aduk antara insight penting dan noise
- tidak jelas mana pola, mana contoh
- sulit dibaca agent secara konsisten

---

## Format Utama yang Disarankan

Best practice untuk source of truth knowledge base adalah:

- **format utama:** structured data, misalnya `JSON`
- **format pendamping:** `.md` untuk review manusia, dokumentasi, dan inspeksi

### Kenapa JSON lebih tepat untuk runtime

Karena sistem perlu:

- mengambil bagian tertentu saja
- membaca pola tertentu dengan cepat
- menjaga struktur tetap konsisten
- meng-update satu bagian tanpa merusak bagian lain

Kalau semua disimpan di `.md` saja, hasilnya:

- mudah dibaca manusia
- tetapi kurang stabil untuk dipakai runtime

Jadi pembagian peran yang sehat adalah:

- `JSON` = source of truth runtime
- `.md` = penjelasan manusia

---

## Isi Minimal Knowledge Base

Knowledge base yang kuat minimal harus punya beberapa lapisan berikut.

### 1. Creator Profile

Berisi gambaran umum tentang kreator.

Tujuannya agar sistem punya konteks dasar sebelum masuk ke pola yang lebih detail.

Contoh isi:

- niche utama
- target audience utama
- persona kreator di depan kamera / di teks
- tone dominan
- worldview kreator saat membahas topik

### 2. Audience Profile

Berisi gambaran audiens yang biasanya dituju kreator.

Contoh isi:

- siapa audiensnya
- keresahan dominan mereka
- desire dominan mereka
- hal yang mereka anggap relate
- bahasa seperti apa yang terasa dekat bagi mereka

### 3. Source Library

Berisi source-source yang paling sering relevan untuk kreator tersebut.

Bukan source generik semua, tetapi source yang:

- berulang
- sering dipakai
- terbukti cocok dengan style kreator

Contoh isi:

- frustration yang sering muncul
- desire yang sering dipakai
- fear yang paling relevan
- trend source yang sering diolah

Bagian ini penting langsung untuk runtime, karena source library adalah salah satu bahan utama saat sistem membuat shortlist source dari query user.

### 4. Observation Patterns

Berisi pola `perilaku`, `emosi`, dan `situasi` yang sering muncul dalam dunia kreator tersebut.

Ini penting supaya sistem tidak memunculkan observasi yang technically benar tetapi terasa bukan gaya kreator.

Contoh isi:

- perilaku khas yang sering diangkat
- emosi khas yang sering dieksplor
- jenis situasi yang sering dipakai sebagai titik observasi

### 5. Moment Patterns

Ini inti yang paling penting untuk tahap momen.

Berisi pola scene yang sering muncul dalam konten kreator.

Contoh isi:

- cara opening
- jenis trigger scene
- bentuk benturan
- ritme eskalasi
- jenis closing
- scene apa yang terasa natural bagi kreator
- scene apa yang tidak cocok

### 6. Voice and Framing

Berisi cara kreator membingkai realita.

Contoh isi:

- cenderung menghakimi atau observasional
- satir atau serius
- emosional atau dingin
- personal atau seperti mengamati orang lain
- suka menampar atau suka mengajak refleksi

### 7. Do / Don't

Bagian ini sangat berguna untuk membatasi generation.

Isi yang dibutuhkan:

- hal yang sering dilakukan kreator
- hal yang jarang atau tidak cocok untuk kreator
- jenis scene yang harus dihindari
- jenis framing yang terasa out of character

---

## Struktur Konseptual yang Paling Sehat

Secara konsep, knowledge base sebaiknya dibangun dari tiga lapisan:

### Layer 1 — Identity

Menjawab:

- kreator ini siapa?
- audiensnya siapa?
- dunia kontennya apa?

### Layer 2 — Pattern

Menjawab:

- source apa yang sering muncul?
- perilaku, emosi, situasi seperti apa yang khas?
- cara melihat manusia seperti apa yang jadi cirinya?

### Layer 3 — Narrative Mechanics

Menjawab:

- scene seperti apa yang natural bagi kreator?
- ritme video seperti apa yang sering dipakai?
- momen seperti apa yang biasanya berhasil?

Kalau tiga layer ini terisi, maka knowledge base sudah cukup kuat untuk dipakai sampai tahap momen.

---

## Bentuk Contoh untuk Runtime

Berikut contoh bentuk knowledge base **secara konsep** dalam format yang cocok untuk runtime.

```json
{
  "creator_profile": {
    "niche": "konten creator journey",
    "persona": "observasional, sedikit nyinyir, ingin terlihat paham",
    "tone": ["tajam", "relatable", "reflektif"],
    "worldview": "banyak orang kelihatan percaya diri, padahal sering digerakkan rasa takut dan ego"
  },
  "audience_profile": {
    "primary_audience": "kreator kecil yang sedang mencoba tumbuh",
    "dominant_pains": [
      "view stagnan",
      "merasa kalah dari kreator lain",
      "bingung kenapa konten tidak naik"
    ],
    "dominant_desires": [
      "ingin terlihat berkembang",
      "ingin dianggap paham",
      "ingin hasil konten terasa sepadan dengan effort"
    ]
  },
  "source_library": {
    "evergreen": [
      "frustration saat performa tidak sesuai ekspektasi",
      "desire untuk terlihat pintar dan berkembang",
      "fear dianggap tidak naik level"
    ],
    "trend_related": [
      "perubahan tren konten",
      "viral format yang memancing perbandingan"
    ]
  },
  "observation_patterns": {
    "behaviors": [
      "cek analytics diam-diam",
      "sok ngajarin orang lain",
      "nyinyir ke konten yang dianggap receh"
    ],
    "emotions": [
      "pede berlebihan",
      "iri tapi gengsi mengakuinya",
      "kesal karena realita tidak mendukung image diri"
    ],
    "situations": [
      "pagi hari setelah upload",
      "saat lihat konten orang lain meledak",
      "sebelum upload konten berikutnya"
    ]
  },
  "moment_patterns": {
    "opening": [
      "scene kecil yang langsung menunjukkan ego atau harapan karakter",
      "scene observasional yang cepat dan relatable"
    ],
    "triggers": [
      "cek analytics",
      "lihat performa orang lain",
      "mendapat pertanyaan dari orang lain"
    ],
    "escalation_style": [
      "dari percaya diri ke defensif",
      "dari santai ke nyinyir",
      "dari berharap ke membuktikan diri"
    ],
    "closing_patterns": [
      "ditutup dengan ironi",
      "ditutup dengan realisasi pahit",
      "ditutup dengan motivasi yang sebenarnya ego-driven"
    ]
  },
  "voice_and_framing": {
    "voice": "tajam, observasional, sedikit satir",
    "framing": [
      "mengamati manusia dari kebiasaan kecil",
      "menunjukkan gap antara image luar dan motivasi dalam"
    ]
  },
  "do_dont": {
    "do": [
      "pakai situasi kecil yang relatable",
      "pakai konflik ego yang halus tapi nyata"
    ],
    "dont": [
      "langsung terlalu motivasional",
      "scene yang terlalu dramatis tanpa dasar observasi",
      "framing yang terlalu heroik"
    ]
  }
}
```

Contoh di atas bukan schema final, tetapi cukup menjelaskan bentuk knowledge base yang sehat:

- tidak berupa raw scripts
- tidak berupa summary panjang tanpa struktur
- berisi pola yang siap dipakai saat generate

---

## Contoh Naratif yang Lebih Mudah Dipahami Manusia

Kalau knowledge base yang sama ingin dibaca manusia, bentuk `.md` pendampingnya bisa terlihat seperti ini:

### Creator Profile

- Kreator membahas perjalanan menjadi content creator kecil yang ingin tumbuh.
- Persona yang muncul: terlihat paham, observasional, sedikit nyinyir, tapi sebenarnya banyak tensi internal.
- Tone dominan: tajam, relatable, reflektif.

### Audience

- Audiens utama adalah kreator kecil yang masih bergulat dengan angka view, validasi, dan rasa tidak stabil.
- Mereka ingin terlihat berkembang, tapi diam-diam masih sangat dipengaruhi hasil performa.

### Source yang Sering Cocok

- frustration saat effort terasa tidak dibalas
- desire untuk terlihat lebih pintar atau lebih jadi
- fear dianggap tidak berkembang

### Pola Observasi yang Khas

**Perilaku**

- sering cek analytics diam-diam
- suka ngajarin orang lain walau dirinya sendiri belum stabil
- suka meremehkan konten orang lain untuk melindungi ego

**Emosi**

- pede berlebihan
- iri tapi gengsi
- kesal karena realita tidak sesuai image diri

**Situasi**

- pagi setelah upload
- saat lihat konten orang lain meledak
- sebelum upload konten berikutnya

### Pola Momen

- pembuka sering dimulai dari momen kecil yang cepat dikenali
- benturan sering datang dari pertemuan antara ekspektasi diri dan realita angka
- penutup sering berupa ironi atau realisasi yang menampar

### Do / Don't

**Do**

- pakai detail kecil yang terasa nyata
- mainkan konflik ego yang tidak terlalu vulgar

**Don't**

- terlalu motivasional
- terlalu dramatis tanpa observasi
- terlalu generik

Contoh `.md` ini tidak ideal sebagai source of truth runtime, tetapi sangat berguna untuk:

- audit manusia
- diskusi internal
- validasi apakah distilasi AI sudah benar atau belum

---

## Best Practice Operasional

### 1. Bangun knowledge base sekali, pakai berkali-kali

Saat user upload sekumpulan script, sistem sebaiknya:

- membaca semuanya
- mengekstrak pola
- menyusun knowledge base

Lalu saat generate ke depan, sistem cukup membaca knowledge base itu, bukan baca ulang semua script mentah.

### 2. Pisahkan ingest dan runtime

Flow sehatnya:

- **ingest phase**: raw scripts -> distilasi -> knowledge base
- **runtime phase**: user query -> knowledge base -> shortlist source -> user pilih source -> generation

Ini membuat flow lebih stabil dan efisien.

### 3. Perlakukan knowledge base sebagai living asset

Knowledge base sebaiknya bisa diperbarui seiring bertambahnya script baru.

Artinya:

- tidak harus dibangun dari nol setiap saat
- bisa di-refresh
- bisa diperbaiki
- bisa dievaluasi kalau output mulai terasa meleset

### 4. Gunakan knowledge base untuk alignment, bukan untuk meniru buta

Tujuan knowledge base bukan menyalin ulang script lama.

Tujuannya adalah:

- memahami pola
- menjaga rasa konten tetap selaras
- memberi fondasi agar ide dan momen baru masih terasa milik kreator

### 5. Fokus utama knowledge base ada di tahap momen

Walaupun knowledge base membantu dari source sampai situasi, manfaat terbesarnya terasa di tahap momen.

Kenapa?

Karena di situlah sistem mulai menentukan:

- scene
- ritme
- urutan kejadian
- cara konflik bergerak

Dan semua itu adalah wilayah yang paling dipengaruhi style kreator.

---

## Ringkasan

Knowledge base terbaik untuk sistem ini adalah:

- hasil distilasi dari script-script kreator
- terstruktur
- berisi pola, bukan sekadar arsip
- dipakai agent saat runtime
- sangat penting terutama untuk alignment pada tahap momen

Secara praktis:

- raw scripts = bahan baku
- knowledge base = hasil pemahaman yang siap dipakai
- runtime generation = memakai knowledge base, bukan membaca ulang semua script mentah

Kalau ingin diringkas ke satu kalimat:

> knowledge base dalam sistem ini adalah creator intelligence layer yang menyimpan pola source, observasi, dan mekanika naratif agar output AI terasa selaras dengan gaya kreator, terutama saat menyusun momen.
