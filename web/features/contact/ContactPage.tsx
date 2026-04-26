'use client'

import type { Route } from 'next'
import Link from 'next/link'
import { useMemo, useState } from 'react'

export function ContactPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')

  const contactHref = useMemo(() => {
    const subject = encodeURIComponent(`ORVIKO - Kontak dari ${name || 'Website'}`)
    const body = encodeURIComponent(`Nama: ${name || '-'}\nEmail: ${email || '-'}\n\nPesan:\n${message || '-'}`)
    return `mailto:rizki@orviko.net?subject=${subject}&body=${body}`
  }, [email, message, name])

  return (
    <main className="legal-page">
      <header className="legal-header">
        <Link href={'/' as Route} className="landing-brand">
          <img src="/branding/logo-orviko.png" alt="Logo ORVIKO" className="landing-brand__mark" />
          <div>
            <strong className="display-font">ORVIKO</strong>
            <span>Contact</span>
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
        <p className="landing-kicker">Contact</p>
        <h1 className="landing-title display-font">Hubungi ORVIKO melalui halaman contact resmi.</h1>
        <p className="landing-subtitle">
          Isi nama, email, dan pesanmu di bawah ini. Setelah itu lanjutkan dengan tombol kirim email.
        </p>
      </section>

      <section className="contact-layout">
        <article className="legal-card">
          <p className="landing-kicker">Informasi</p>
          <h2 className="display-font">Kontak aktif saat ini</h2>
          <p>Email utama yang digunakan untuk komunikasi layanan dan operasional adalah `rizki@orviko.net`.</p>
        </article>

        <form className="contact-form-card">
          <label className="site-footer-form__field">
            <span>Nama</span>
            <input type="text" value={name} onChange={(event) => setName(event.target.value)} placeholder="Nama kamu" />
          </label>

          <label className="site-footer-form__field">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="email@kamu.com"
            />
          </label>

          <label className="site-footer-form__field site-footer-form__field--full">
            <span>Pesan</span>
            <textarea
              rows={6}
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Tulis pertanyaan, kebutuhan, atau pesanmu di sini."
            />
          </label>

          <div className="site-footer-form__actions">
            <a href={contactHref} className="btn btn-primary btn-large">
              Kirim via Email
            </a>
            <p>Tujuan email: rizki@orviko.net</p>
          </div>
        </form>
      </section>
    </main>
  )
}
