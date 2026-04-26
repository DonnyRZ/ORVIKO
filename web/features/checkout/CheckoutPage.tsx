import type { Route } from 'next'
import Link from 'next/link'

type Plan = {
  name: string
  price: string
  tag: string
  features: string[]
}

const plans: Plan[] = [
  {
    name: 'Starter',
    price: 'Rp 79.000',
    tag: 'Untuk mulai membangun gaya script',
    features: [
      '1 workspace creator profile.',
      'Upload script referensi dasar.',
      'Analisis gaya bahasa kreator.',
      'Analisis pola opening dan hook.',
      'Analisis keresahan dan tema yang sering muncul.',
      'Draft script berbasis persona kreator.',
      'Rekomendasi source atau angle konten.',
      'Rekomendasi perilaku, emosi, dan situasi.',
      'Penyusunan momen video awal.',
      'Histori draft script.',
      'Cocok untuk validasi awal gaya konten.',
    ],
  },
  {
    name: 'Creator',
    price: 'Rp 199.000',
    tag: 'Untuk kreator yang sudah rutin produksi',
    features: [
      'Semua fitur Starter.',
      'Kapasitas referensi script lebih besar.',
      'Persona kreator lebih detail.',
      'Variasi angle konten lebih banyak.',
      'Regenerate draft dengan arah berbeda.',
      'Workspace postingan gambar.',
      'Generate visual postingan dari teks.',
      'Pilihan aspect ratio visual.',
      'Embed logo atau gambar referensi.',
      'Histori hasil visual.',
      'Cocok untuk kreator yang rutin produksi konten.',
    ],
  },
  {
    name: 'Pro',
    price: 'Rp 499.000',
    tag: 'Untuk workflow yang lebih serius',
    features: [
      'Semua fitur Creator.',
      'Kapasitas workspace lebih besar.',
      'Analisis persona dan gaya konten lebih mendalam.',
      'Rekomendasi script untuk beberapa format konten.',
      'Eksplorasi banyak opsi angle per task.',
      'Output draft lebih siap untuk produksi.',
      'Prioritas untuk workflow script dan visual.',
      'Manajemen histori lebih panjang.',
      'Cocok untuk kreator serius, tim kecil, atau brand personal.',
      'Support setup awal via email.',
      'Akses fitur lanjutan saat tersedia di fase berikutnya.',
    ],
  },
]

const buildMailto = (plan: Plan) => {
  const subject = encodeURIComponent(`ORVIKO - Saya tertarik paket ${plan.name}`)
  const body = encodeURIComponent(
    `Halo,\n\nSaya tertarik dengan paket ${plan.name} (${plan.price}).\nMohon info langkah berikutnya untuk aktivasi.\n\nTerima kasih.`
  )
  return `mailto:avvkun@gmail.com?subject=${subject}&body=${body}`
}

export function CheckoutPage() {
  return (
    <main className="checkout-page">
      <header className="checkout-header">
        <Link href={'/' as Route} className="landing-brand">
          <img src="/branding/logo-orviko.png" alt="Logo ORVIKO" className="landing-brand__mark" />
          <div>
            <strong className="display-font">ORVIKO</strong>
            <span>Checkout V1</span>
          </div>
        </Link>

        <div className="checkout-header__actions">
          <Link href={'/' as Route} className="btn btn-ghost">
            Kembali ke landing
          </Link>
          <a href="mailto:avvkun@gmail.com" className="btn btn-outline">
            Email langsung
          </a>
        </div>
      </header>

      <section className="checkout-hero">
        <p className="landing-kicker">Pilih paket</p>
        <h1 className="landing-title display-font">Mulai dari paket yang paling pas dengan ritme produksi kontenmu.</h1>
        <p className="landing-subtitle">
          Untuk tahap ini, checkout belum terhubung ke payment gateway. Setelah pilih paket, kamu akan diarahkan
          ke email agar proses aktivasi awal bisa dibantu manual.
        </p>
      </section>

      <section className="checkout-grid">
        {plans.map((plan, index) => (
          <article key={plan.name} className={`checkout-card ${index === 1 ? 'checkout-card--featured' : ''}`}>
            <div className="checkout-card__top">
              <div>
                <p className="checkout-card__eyebrow">{plan.tag}</p>
                <h2 className="display-font">{plan.name}</h2>
              </div>
              <div className="checkout-card__price">{plan.price}</div>
            </div>

            <ul className="checkout-card__list">
              {plan.features.map((feature) => (
                <li key={feature}>{feature}</li>
              ))}
            </ul>

            <a href={buildMailto(plan)} className={`btn ${index === 1 ? 'btn-primary' : 'btn-outline'} btn-large`}>
              Pilih {plan.name}
            </a>
          </article>
        ))}
      </section>

      <section className="checkout-note">
        <p>
          Aktivasi tahap awal dibantu lewat email <strong>avvkun@gmail.com</strong>. Jadi alurnya masih landing
          page ke checkout, lalu lanjut komunikasi manual sebelum tahap pembayaran penuh diintegrasikan.
        </p>
      </section>
    </main>
  )
}
