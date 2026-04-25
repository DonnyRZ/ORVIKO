# Source sampai Situasi

Dokumen ini merekap pendekatan yang benar untuk empat komponen awal dalam flow ide konten:

1. `Source`
2. `Perilaku`
3. `Emosi`
4. `Situasi`

Fokus dokumen ini hanya pada empat komponen tersebut. Dokumen ini sengaja tidak membahas tahap berikutnya seperti momen, enhance, atau output akhir, karena tujuan utamanya adalah mengunci fondasi berpikir yang benar terlebih dahulu.

## Tujuan Utama

Empat komponen ini dipakai untuk mengubah bahan mentah menjadi dasar observasi yang hidup, tajam, dan dekat dengan realita manusia. Kalau bagian ini benar, maka tahap berikutnya akan punya bahan baku yang kuat. Kalau bagian ini salah, maka output selanjutnya akan terasa generik, kaku, dan seperti template.

Kesalahan paling umum adalah memperlakukan komponen-komponen ini sebagai field analitis yang kaku. Pendekatan yang benar justru sebaliknya: komponen ini harus terasa manusiawi, konkret, dan mudah dibayangkan sebagai bagian dari kehidupan nyata.

## 1. Source

`Source` adalah titik masuk utama untuk eksplorasi ide. Source bukan sekadar kategori besar, dan bukan label abstrak yang terlalu umum. Source harus terasa seperti sumber ketegangan, sumber rasa, sumber perhatian, atau sumber relevansi yang nyata.

### Peran source dalam flow

Dalam flow fitur ini, `source` bukan hasil akhir. Source adalah titik mulai yang dipakai untuk membuka arah eksplorasi.

Secara fungsi, source dipakai untuk:

- menentukan dari sudut mana topik akan dibedah
- memberi jalur observasi untuk perilaku, emosi, dan situasi
- membantu sistem dan user sepakat dulu tentang “masalah ini sebenarnya sedang dilihat dari mana”

Jadi pemilihan source adalah salah satu keputusan paling awal dan paling penting dalam flow asisten.

### Cara pikir yang benar

Source harus menjawab pertanyaan:

- kita sedang membahas dorongan atau ketegangan dari mana?
- hal apa yang sedang jadi sumber rasa sakit, rasa ingin, rasa takut, rasa kesal, rasa penasaran, atau rasa relevan?
- apa titik awal yang cukup spesifik untuk diturunkan lebih jauh?

Jadi source bukan cuma:

- `frustration`
- `fear`
- `desire`

Kalau berhenti di situ, hasilnya masih terlalu abstrak.

Yang benar adalah source yang sudah terasa hidup, misalnya:

- frustration: orang merasa kontennya serius tapi tidak pernah meledak
- desire: pengen kelihatan jago tanpa harus terlihat capek belajar
- fear: takut dianggap tidak berkembang walaupun sudah rutin upload
- behavior: kebiasaan ikut-ikutan format konten orang lain
- moment: momen beberapa menit sebelum klik upload

### Prinsip penting

- Source harus spesifik enough untuk dibayangkan.
- Source harus punya tensi.
- Source harus bisa diturunkan ke observasi yang lebih kecil.
- Source tidak boleh terlalu generik sampai bisa berlaku untuk semua orang tanpa warna.

### Metode pemilihan source

Secara best practice, source sebaiknya **tidak muncul secara random** dan juga **tidak langsung diputuskan diam-diam oleh sistem tanpa transparansi**.

Metode yang paling sehat adalah:

1. user memberi task atau query
2. sistem membaca knowledge base kreator
3. sistem mencocokkan query user dengan:
   - audience profile
   - source library yang sering dipakai kreator
   - pola topik yang relevan dengan dunia kreator
4. sistem membuat shortlist beberapa source yang paling masuk akal
5. agent menampilkan shortlist itu ke user
6. user memilih salah satu source, atau menulis source sendiri lewat free text

Dengan cara ini:

- sistem tetap aktif membantu
- user tetap punya kontrol
- source yang dipilih tetap relevan terhadap gaya kreator

### Kenapa source perlu dipilih, bukan langsung ditetapkan diam-diam

Karena satu query user bisa dibuka dari banyak sudut.

Contoh:

kalau user ingin bahas topik seputar konten kreator yang performanya mandek, sistem bisa saja melihatnya dari:

- keresahan
- frustrasi
- desire untuk terlihat berkembang
- fear dianggap tidak naik level
- behavior tertentu yang berulang

Kalau sistem langsung memilih satu source tanpa memberi user visibilitas, ada risiko:

- source-nya technically valid
- tetapi tidak sesuai arah yang sebenarnya ingin diambil user

Jadi best practice-nya:

- sistem membantu memilih
- user tetap bisa mengunci arah

### Bentuk output source yang paling tepat

Source yang ditampilkan ke user sebaiknya berbentuk:

- spesifik
- pendek
- punya tensi
- mudah dipahami dalam sekali baca

Contoh bentuk opsi yang tepat:

- `Frustration: sudah niat bikin konten, tapi hasilnya kalah sama konten yang lebih ringan`
- `Fear: takut dianggap tidak berkembang walaupun sudah rutin upload`
- `Desire: ingin terlihat paham soal konten di depan orang lain`

Bukan:

- `frustration`
- `fear`
- `desire`

Karena label polos seperti itu belum cukup membantu user mengambil keputusan.

### Salah vs benar

Kurang tepat:

- `konten creator`
- `TikTok`
- `motivasi bikin konten`

Lebih tepat:

- `keresahan kreator yang views-nya selalu mentok`
- `ketakutan saat performa konten turun terus`
- `keinginan terlihat pintar di depan audiens`
- `frustrasi saat konten yang niat kalah sama konten yang ringan`

## 2. Perilaku

`Perilaku` adalah apa yang dilakukan orang itu di dunia nyata. Bukan teori kepribadian, bukan analisis psikologis yang kaku, dan bukan ringkasan moral. Perilaku harus observasional.

### Cara pikir yang benar

Perilaku harus menjawab pertanyaan:

- orang ini ngapain?
- apa kebiasaan kecilnya?
- apa yang dia ucapkan, tunjukkan, ulangi, atau lakukan?
- kalau dilihat dari luar, apa yang kelihatan?

Perilaku yang kuat biasanya bisa divisualisasikan. Saat dibaca, orang langsung kebayang adegannya.

### Ciri perilaku yang benar

- konkret
- bisa diamati
- terasa seperti kebiasaan atau tindakan nyata
- dekat dengan bahasa sehari-hari

### Yang perlu dihindari

Jangan terlalu abstrak seperti:

- `kurang percaya diri`
- `butuh validasi`
- `punya insecurity`

Itu lebih dekat ke interpretasi, belum ke perilaku.

Kalau mau benar, ubah ke bentuk yang bisa dilihat:

- sering buka ulang analytics beberapa menit sekali
- upload sambil bilang “coba aja dulu”, tapi semalaman tetap mantengin view
- suka nyindir kreator lain yang kontennya dianggap dangkal
- bikin caption seolah santai, padahal sangat ingin dipuji

### Prinsip penting

- Perilaku harus terasa seperti pengamatan.
- Perilaku yang bagus bisa divisualisasikan.
- Perilaku lebih kuat kalau ditulis dalam bahasa natural, bukan bahasa teori.

## 3. Emosi

`Emosi` adalah rasa yang hidup di dalam konteks itu. Tapi emosi di sini tidak boleh diperlakukan sebagai daftar emosi generik yang datar. Emosi harus terasa pas dengan karakter source dan perilakunya.

### Cara pikir yang benar

Emosi harus menjawab pertanyaan:

- sebenarnya rasa apa yang sedang hidup di balik perilaku itu?
- emosi apa yang mendorong tindakan mereka?
- rasa apa yang membuat topik ini relatable?

Emosi tidak harus selalu dramatis. Emosi bisa halus, tapi tetap spesifik.

### Yang perlu dihindari

Kurang kuat:

- sedih
- takut
- marah
- senang

Itu terlalu generik kalau berdiri sendirian.

Lebih kuat:

- iri tapi gengsi mengakuinya
- kesal karena merasa sudah lebih niat dari orang lain
- pede berlebihan
- malu setengah mati tapi sok santai
- capek, tapi tetap tidak mau berhenti

### Prinsip penting

- Emosi harus terasa manusiawi.
- Emosi harus cocok dengan source dan perilaku.
- Emosi sebaiknya tidak terlalu “kamus”, tetapi lebih terasa seperti rasa yang benar-benar dialami.

## 4. Situasi

`Situasi` adalah konteks atau momen konkret saat perilaku dan emosi itu muncul. Situasi bukan tema besar. Situasi harus terasa seperti adegan.

### Cara pikir yang benar

Situasi harus menjawab pertanyaan:

- kapan ini terjadi?
- di kondisi seperti apa ini muncul?
- momen spesifik apa yang membuat perilaku dan emosi itu aktif?

Situasi yang baik membuat ide jadi dekat ke kehidupan nyata, karena user bisa langsung membayangkan kapan hal itu terjadi.

### Yang perlu dihindari

Kurang tepat:

- `di media sosial`
- `saat bikin konten`
- `ketika sedang sedih`

Itu masih terlalu luas.

Lebih tepat:

- beberapa menit sebelum upload
- setelah lihat view stagnan padahal sudah optimis
- saat buka FYP dan lihat orang lain meledak dengan konten yang terasa lebih ringan
- malam hari setelah seharian nunda rekam
- pas lagi siap-siap syuting tapi mendadak ragu sendiri

### Prinsip penting

- Situasi harus terasa seperti adegan kecil.
- Situasi yang baik membuat topik lebih visual dan lebih relatable.
- Semakin konkret situasinya, semakin mudah tahap berikutnya berkembang dengan baik.

## Hubungan antar empat komponen

Urutannya tidak berdiri sendiri. Empat komponen ini saling menguatkan:

- `Source` memberi titik masuk
- `Perilaku` memberi tanda yang bisa diamati
- `Emosi` memberi rasa
- `Situasi` memberi panggung kejadian

Kalau source bagus tapi perilaku lemah, hasilnya terasa abstrak.
Kalau perilaku bagus tapi situasinya lemah, hasilnya terasa tidak hidup.
Kalau emosi terlalu generik, hasilnya terasa datar.

Jadi targetnya bukan sekadar mengisi empat kotak, tetapi membentuk satu observasi manusia yang utuh.

## Contoh detail

Contoh berikut hanya sampai `Source`, `Perilaku`, `Emosi`, dan `Situasi`.

### Contoh 1

**Source**

`Frustration: orang yang merasa kontennya sudah niat dan “berisi”, tapi performanya selalu kalah sama konten yang lebih ringan`

Kenapa ini bagus:

- ada tensi
- ada rasa tidak adil
- langsung terasa dunia nyatanya
- cukup spesifik untuk diturunkan

**Perilaku**

- tiap habis upload suka bilang, “padahal ini isinya daging semua”
- sering membandingkan kontennya dengan kreator lain yang dianggap lebih receh
- mantengin analytics diam-diam, walaupun di depan orang lain sok santai
- mulai sering menyelipkan nada nyinyir saat ngomongin konten viral

Kenapa ini bagus:

- bisa dibayangkan
- terasa seperti orang nyata
- bukan bahasa teori

**Emosi**

- kesal
- iri tapi gengsi mengakui
- merasa dirinya lebih niat dari orang lain
- capek karena ekspektasinya tidak ketemu hasil

Kenapa ini bagus:

- emosinya tidak datar
- cocok dengan perilaku
- ada rasa yang lebih spesifik dari sekadar “sedih” atau “marah”

**Situasi**

- beberapa jam setelah upload, saat view tidak bergerak
- saat buka FYP dan lihat konten ringan orang lain justru meledak
- ketika menjelaskan ke orang lain kenapa kontennya “sebenarnya bagus”
- malam hari setelah upload, waktu sendirian dan mulai overthinking

Kenapa ini bagus:

- semua situasi terasa seperti adegan
- mudah divisualisasikan
- cukup sempit untuk jadi bahan observasi yang hidup

### Contoh 2

**Source**

`Desire: orang yang ingin terlihat sudah “jadi kreator serius”, padahal sebenarnya masih sangat butuh validasi dari performa kontennya`

**Perilaku**

- sering bicara seolah sudah punya sistem konten yang matang
- suka kasih saran ke orang lain dengan nada yakin
- memilih upload yang aman supaya tidak terlihat gagal
- menghapus konten yang menurutnya bikin image-nya turun

**Emosi**

- ingin dianggap kompeten
- takut terlihat belum jadi
- pede di luar, rapuh di dalam
- haus pengakuan tapi tidak mau kelihatan butuh

**Situasi**

- saat menjawab pertanyaan followers seolah paling paham
- sebelum upload konten yang sebenarnya dia sendiri belum yakin
- ketika performa konten turun dan mulai merasa image-nya ikut turun
- saat lihat kreator lain tumbuh lebih cepat dari dirinya

### Catatan akhir

Kalau empat komponen ini ditulis dengan benar, maka hasilnya tidak lagi terasa seperti template brainstorming. Hasilnya akan terasa seperti hasil pengamatan terhadap manusia, dan itu yang membuat fondasi ide konten menjadi jauh lebih kuat.

Tambahan penting untuk tahap awal flow:

Sebelum sampai ke perilaku, emosi, dan situasi, sistem harus lebih dulu memilih source yang paling tepat. Karena itu, kualitas pemilihan source akan sangat mempengaruhi kualitas tiga komponen setelahnya.
