import type { Route } from 'next'
import Link from 'next/link'

const sections = [
  {
    title: 'Layanan ORVIKO',
    body:
      'ORVIKO menyediakan layanan digital untuk membantu kreator menyusun draft script dan materi visual sesuai paket yang dipilih pengguna.',
  },
  {
    title: 'Akun Pengguna',
    body:
      'Pengguna bertanggung jawab atas keakuratan data akun yang digunakan untuk login, menjaga keamanan akses akun, dan menggunakan layanan secara sah serta tidak melanggar hukum yang berlaku.',
  },
  {
    title: 'Paket dan Pembayaran',
    body:
      'Informasi paket, harga, dan pembayaran layanan ORVIKO ditampilkan dalam Rupiah. Pengguna wajib meninjau detail paket dan informasi transaksi sebelum melanjutkan proses pembayaran.',
  },
  {
    title: 'Penggunaan Konten',
    body:
      'Pengguna bertanggung jawab penuh atas materi, referensi, dan instruksi yang diunggah ke ORVIKO, termasuk memastikan bahwa konten tersebut tidak melanggar hak pihak lain.',
  },
  {
    title: 'Perubahan Layanan',
    body:
      'ORVIKO dapat menyesuaikan fitur, tampilan, maupun alur layanan dari waktu ke waktu untuk kebutuhan pengembangan produk dan operasional.',
  },
  {
    title: 'Pembatalan dan Pengembalian',
    body:
      'Permohonan pembatalan transaksi atau pengembalian dana akan ditinjau berdasarkan jenis layanan, status transaksi, dan kebijakan operasional ORVIKO yang berlaku pada saat permohonan diajukan.',
  },
  {
    title: 'Privasi Data',
    body:
      'Data dasar akun seperti nama, email, dan foto profil dapat digunakan untuk kebutuhan autentikasi, identifikasi akun, dan pengelolaan layanan di dalam sistem ORVIKO.',
  },
  {
    title: 'Kontak',
    body:
      'Untuk pertanyaan terkait layanan, pengguna dapat menghubungi ORVIKO melalui email di rizki@orviko.net.',
  },
]

export function TermsPage() {
  return (
    <main className="legal-page">
      <header className="legal-header">
        <Link href={'/' as Route} className="landing-brand">
          <img src="/branding/logo-orviko.png" alt="Logo ORVIKO" className="landing-brand__mark" />
          <div>
            <strong className="display-font">ORVIKO</strong>
            <span>Terms & Conditions</span>
          </div>
        </Link>

        <div className="legal-header__actions">
          <Link href={'/' as Route} className="btn btn-ghost">
            Kembali ke landing
          </Link>
          <Link href={'/checkout' as Route} className="btn btn-outline">
            Lihat checkout
          </Link>
        </div>
      </header>

      <section className="legal-hero">
        <p className="landing-kicker">Syarat & Ketentuan</p>
        <h1 className="landing-title display-font">Ketentuan penggunaan layanan ORVIKO.</h1>
        <p className="landing-subtitle">
          Halaman ini menjelaskan ketentuan dasar penggunaan layanan ORVIKO untuk kebutuhan informasi pengguna dan
          kelengkapan operasional website.
        </p>
        <div className="legal-meta">
          <span>Terakhir diperbarui: 26 April 2026</span>
          <a href="mailto:rizki@orviko.net">Kontak: rizki@orviko.net</a>
        </div>
      </section>

      <section className="legal-sections">
        {sections.map((section) => (
          <article key={section.title} className="legal-card">
            <h2 className="display-font">{section.title}</h2>
            <p>{section.body}</p>
          </article>
        ))}
      </section>

      <section className="legal-contact-card">
        <div>
          <p className="landing-kicker">Butuh bantuan?</p>
          <h2 className="display-font">Hubungi ORVIKO melalui email resmi yang sedang aktif.</h2>
          <p>
            Untuk pertanyaan layanan, klarifikasi paket, atau kebutuhan operasional lain, silakan gunakan kontak di
            bawah ini.
          </p>
        </div>
        <a href="mailto:rizki@orviko.net" className="btn btn-primary btn-large">
          rizki@orviko.net
        </a>
      </section>
    </main>
  )
}
