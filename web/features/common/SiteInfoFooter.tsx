import type { Route } from 'next'
import Link from 'next/link'

export function SiteInfoFooter() {
  return (
    <section className="site-footer-card">
      <div className="site-footer-card__top">
        <article className="site-footer-card__brand">
          <p className="site-footer-card__eyebrow">Informasi Bisnis</p>
          <h2 className="display-font">ORVIKO</h2>
          <p>
            Layanan digital untuk membantu kreator menyusun script dan materi visual dengan alur yang lebih cepat,
            lebih fokus, dan lebih terarah.
          </p>
        </article>

        <Link href={'/contact' as Route} className="site-footer-card__link">
          <span className="site-footer-card__eyebrow">Contact</span>
          <strong>Hubungi ORVIKO</strong>
          <p>Buka halaman contact untuk isi nama, email, dan pesan.</p>
        </Link>

        <Link href={'/terms' as Route} className="site-footer-card__link">
          <span className="site-footer-card__eyebrow">Terms & Conditions</span>
          <strong>Lihat ketentuan layanan</strong>
          <p>Buka halaman terms untuk membaca syarat dan ketentuan lengkap.</p>
        </Link>
      </div>
    </section>
  )
}
