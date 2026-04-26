'use client'

import type { Route } from 'next'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'

const planMap = {
  starter: 'Starter',
  creator: 'Creator',
  pro: 'Pro',
}

export function PaymentPage() {
  const searchParams = useSearchParams()
  const planSlug = searchParams.get('plan') ?? 'creator'
  const planName = planMap[planSlug as keyof typeof planMap] ?? 'Creator'
  const price = searchParams.get('price') ?? 'Rp 199.000'
  const loginStatus = searchParams.get('login')
  const email = searchParams.get('email') ?? ''

  return (
    <main className="payment-page">
      <header className="payment-header">
        <Link href={'/' as Route} className="landing-brand">
          <img src="/branding/logo-orviko.png" alt="Logo ORVIKO" className="landing-brand__mark" />
          <div>
            <strong className="display-font">ORVIKO</strong>
            <span>Payment V1</span>
          </div>
        </Link>

        <div className="payment-header__actions">
          <Link href={'/' as Route} className="btn btn-ghost">
            Kembali ke landing
          </Link>
          <Link href={'/checkout' as Route} className="btn btn-outline">
            Lihat checkout
          </Link>
        </div>
      </header>

      {loginStatus === 'success' ? (
        <div className="payment-login-banner">
          <strong>Login berhasil</strong>
          <span>{email || 'Akun Google berhasil terhubung ke flow payment.'}</span>
        </div>
      ) : null}

      <section className="payment-stage">
        <div className="payment-stage__copy">
          <p className="landing-kicker">Payment Dummy</p>
          <h1 className="payment-stage__title display-font">Lanjutkan pembayaran paket {planName}.</h1>
          <p className="payment-stage__body">
            Halaman ini hanya untuk menguji alur checkout dan login sebelum payment gateway asli diintegrasikan.
          </p>
        </div>
        <div className="payment-panel">
          <div className="payment-panel__top">
            <div>
              <p className="checkout-card__eyebrow">Order Summary</p>
              <h2 className="display-font">{planName}</h2>
            </div>
            <span className="tag tag-accent">Dummy payment</span>
          </div>

          <div className="payment-amount">
            <strong>{price}</strong>
            <span>Pembayaran satu kali</span>
          </div>

          <div className="payment-summary">
            <div className="payment-summary__row">
              <span>Paket</span>
              <strong>{planName}</strong>
            </div>
            <div className="payment-summary__row">
              <span>Tagihan</span>
              <strong>{price}</strong>
            </div>
            <div className="payment-summary__row">
              <span>Mode</span>
              <strong>Simulasi</strong>
            </div>
            {email ? (
              <div className="payment-summary__row">
                <span>Akun</span>
                <strong>{email}</strong>
              </div>
            ) : null}
          </div>

          <button type="button" className="btn btn-primary btn-large payment-panel__cta">
            Bayar Dummy
          </button>

          <p className="payment-panel__hint">
            Tombol ini belum menjalankan transaksi apa pun. Ini hanya placeholder untuk membentuk pengalaman payment.
          </p>
        </div>
      </section>

      <section className="payment-note">
        <p>
          Status pembayaran belum disimpan sebagai transaksi final. Tahap berikutnya tinggal menyambungkan tombol bayar
          ke halaman selesai atau payment gateway asli.
        </p>
      </section>
    </main>
  )
}
