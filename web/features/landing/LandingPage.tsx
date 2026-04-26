'use client'

import type { Route } from 'next'
import Link from 'next/link'
import { useState } from 'react'

const scriptBenefits = [
  'Belajar dari script yang kamu upload agar output baru terasa tetap satu suara dengan gayamu.',
  'Mengenali pola opening, keresahan, punchline, dan ritme penjelasan yang sering kamu pakai.',
  'Membantu kamu mulai dari angle sampai draft awal tanpa terasa seperti template AI generik.',
]

const visualBenefits = [
  'Ubah teks sederhana jadi visual postingan yang siap dipakai tanpa desain dari nol.',
  'Pilih aspect ratio sesuai kebutuhan canvas, bukan terkunci ke satu platform saja.',
  'Masukkan logo atau gambar referensi agar hasil visual lebih sesuai brand-mu.',
]

const faqs = [
  {
    question: 'Apa ORVIKO sebenarnya membantu bikin script atau cuma kasih ide?',
    answer:
      'Arah utamanya adalah membantu kreator sampai ke draft script yang terasa sesuai gaya kontennya. Ide hanyalah pintu masuk, bukan output akhirnya.',
  },
  {
    question: 'Kenapa perlu upload script lama?',
    answer:
      'Karena di situlah ORVIKO membaca pola bahasa, struktur cerita, keresahan, dan persona yang selama ini sudah kamu bangun sebagai kreator.',
  },
  {
    question: 'Apakah ORVIKO juga bisa bantu visual postingan?',
    answer:
      'Bisa. Dari teks sederhana, ORVIKO bisa mempercepat pembuatan visual postingan agar kamu tidak mulai dari canvas kosong setiap kali produksi.',
  },
  {
    question: 'Apakah checkout ini sudah langsung bayar otomatis?',
    answer:
      'Belum. Untuk V1, kamu memilih paket lalu menghubungi email yang tersedia agar proses aktivasi awal bisa dibantu manual.',
  },
]

const heroModes = {
  script: {
    label: 'Script',
    title: 'Asisten script yang paham gaya kontenmu',
    body:
      'ORVIKO belajar dari script yang kamu upload, lalu membantu menyusun draft baru yang tetap dekat dengan ritme, persona, dan gaya bicaramu.',
    image: '/landing/orviko-script.png',
    alt: 'Tampilan workspace script ORVIKO',
  },
  visual: {
    label: 'Visual',
    title: 'Visual postingan siap pakai dari teks sederhana',
    body:
      'Masuk ke workspace visual untuk mengubah teks menjadi postingan yang rapi, cepat diproduksi, dan tetap bisa diarahkan sesuai kebutuhan brand.',
    image: '/landing/orviko-slide.png',
    alt: 'Tampilan workspace visual ORVIKO',
  },
} as const

type HeroMode = keyof typeof heroModes

export function LandingPage() {
  const [heroMode, setHeroMode] = useState<HeroMode>('script')
  const activeHero = heroModes[heroMode]

  return (
    <main className="landing-page">
      <header className="landing-nav">
        <Link href={'/' as Route} className="landing-brand">
          <img src="/branding/logo-orviko.png" alt="Logo ORVIKO" className="landing-brand__mark" />
          <div>
            <strong className="display-font">ORVIKO</strong>
            <span>Creative OS untuk script dan visual</span>
          </div>
        </Link>

        <div className="landing-nav__actions">
          <a href="#cara-kerja" className="btn btn-ghost">
            Lihat cara kerja
          </a>
          <Link href={'/checkout' as Route} className="btn btn-primary">
            Pilih Paket
          </Link>
        </div>
      </header>

      <section className="landing-hero landing-hero--stacked">
        <div className="landing-hero__copy landing-hero__copy--wide">
          <p className="landing-kicker">Asisten personal untuk kreator</p>
          <h1 className="landing-title display-font">
            AI yang bantu bikin script tetap terasa seperti kamu
          </h1>
          <p className="landing-subtitle">
            ORVIKO membantu kreator membangun draft script dari gaya konten yang sudah mereka miliki, lalu
            mempercepat pembuatan visual postingan dari teks sederhana.
          </p>

          <div className="landing-cta-row">
            <Link href={'/checkout' as Route} className="btn btn-primary btn-large">
              Pilih Paket
            </Link>
            <a href="#value" className="btn btn-outline btn-large">
              Kenapa ini berguna
            </a>
          </div>

          <div className="landing-proof">
            <span>Belajar dari script yang kamu upload</span>
            <span>Draft script yang lebih personal</span>
            <span>Visual postingan lebih cepat dibuat</span>
          </div>
        </div>

        <div className="landing-showcase landing-showcase--hero">
          <div className="landing-showcase__tabs" role="tablist" aria-label="Mode workspace">
            {(Object.keys(heroModes) as HeroMode[]).map((mode) => (
              <button
                key={mode}
                type="button"
                role="tab"
                aria-selected={heroMode === mode}
                className={`landing-showcase__tab ${heroMode === mode ? 'is-active' : ''}`}
                onClick={() => setHeroMode(mode)}
              >
                {heroModes[mode].label}
              </button>
            ))}
          </div>

          <div className="landing-hero-note">
            <p className="landing-pane__eyebrow">{activeHero.label} workspace</p>
            <h2 className="display-font">{activeHero.title}</h2>
            <p>{activeHero.body}</p>
          </div>

          <div className="landing-window landing-window--hero">
            <div className="landing-window__bar">
              <span />
              <span />
              <span />
            </div>
            <div className="landing-window__hero-body">
              <img src={activeHero.image} alt={activeHero.alt} className="landing-window__hero-image" />
            </div>
          </div>
        </div>
      </section>

      <section id="value" className="landing-section landing-section--split">
        <div className="landing-section__intro">
          <p className="landing-kicker">Value utama</p>
          <h2 className="landing-section__title display-font">Dua masalah utama kreator, satu workspace yang lebih fokus.</h2>
          <p className="landing-section__body">
            ORVIKO tidak mencoba menjadi segalanya. Fokusnya adalah membantu kreator menulis lebih personal dan
            memproduksi visual lebih cepat.
          </p>
        </div>

        <div className="landing-feature-grid">
          <article className="landing-feature-card">
            <p className="landing-feature-card__eyebrow">Script</p>
            <h3 className="display-font">Asisten script yang paham gaya kontenmu</h3>
            <ul className="landing-list">
              {scriptBenefits.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>

          <article className="landing-feature-card landing-feature-card--soft">
            <p className="landing-feature-card__eyebrow">Visual</p>
            <h3 className="display-font">Visual postingan siap pakai dari teks sederhana</h3>
            <ul className="landing-list">
              {visualBenefits.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            <div className="landing-shot landing-shot--compact">
              <img
                src="/landing/orviko-slide.png"
                alt="Tampilan workspace visual postingan ORVIKO"
                className="landing-shot__image"
              />
            </div>
          </article>
        </div>
      </section>

      <section id="cara-kerja" className="landing-section">
        <div className="landing-section__intro landing-section__intro--center">
          <p className="landing-kicker">Cara kerja</p>
          <h2 className="landing-section__title display-font">Dari script lama sampai draft baru yang terasa tetap milikmu.</h2>
        </div>

        <div className="landing-steps">
          <article className="landing-step">
            <span>01</span>
            <h3>Upload script referensi</h3>
            <p>ORVIKO membaca pola bahasa, pembuka, keresahan, dan cara kamu menyusun cerita.</p>
          </article>
          <article className="landing-step">
            <span>02</span>
            <h3>Bangun creator profile</h3>
            <p>Gaya bicara dan persona kreator dirangkum jadi fondasi untuk task berikutnya.</p>
          </article>
          <article className="landing-step">
            <span>03</span>
            <h3>Susun draft script</h3>
            <p>Task baru diproses dengan arah yang lebih personal, bukan sekadar hasil AI generik.</p>
          </article>
          <article className="landing-step">
            <span>04</span>
            <h3>Lanjut ke visual</h3>
            <p>Dari teks sederhana, workspace slide membantu mempercepat pembuatan visual postingan.</p>
          </article>
        </div>
      </section>

      <section className="landing-section landing-section--faq">
        <div className="landing-section__intro">
          <p className="landing-kicker">FAQ</p>
          <h2 className="landing-section__title display-font">Hal penting sebelum mulai.</h2>
        </div>

        <div className="landing-faq">
          {faqs.map((item) => (
            <details key={item.question} className="landing-faq__item">
              <summary>{item.question}</summary>
              <p>{item.answer}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="landing-cta">
        <div>
          <p className="landing-kicker">Mulai dari paket yang sesuai</p>
          <h2 className="landing-section__title display-font">Kalau gaya konten itu aset, proses nulisnya juga seharusnya personal.</h2>
        </div>
        <div className="landing-cta__actions">
          <Link href={'/checkout' as Route} className="btn btn-primary btn-large">
            Lihat Paket
          </Link>
          <a className="btn btn-ghost btn-large" href="mailto:avvkun@gmail.com">
            Hubungi via Email
          </a>
        </div>
      </section>
    </main>
  )
}
