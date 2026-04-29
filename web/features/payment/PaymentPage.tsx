'use client'

import { useEffect, useMemo, useState } from 'react'
import type { Route } from 'next'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { SiteInfoFooter } from '@/features/common/SiteInfoFooter'
import { buildApiUrl } from '@/lib/api'

const planMap = {
  starter: 'Starter',
  creator: 'Creator',
  pro: 'Pro',
}

const MIDTRANS_CLIENT_KEY = process.env.NEXT_PUBLIC_MIDTRANS_CLIENT_KEY ?? ''

declare global {
  interface Window {
    snap?: {
      pay: (
        token: string,
        options?: {
          onSuccess?: (result: unknown) => void
          onPending?: (result: unknown) => void
          onError?: (result: unknown) => void
          onClose?: () => void
        }
      ) => void
    }
  }
}

export function PaymentPage() {
  const searchParams = useSearchParams()
  const planSlug = searchParams.get('plan') ?? 'creator'
  const planName = planMap[planSlug as keyof typeof planMap] ?? 'Creator'
  const priceLabel = searchParams.get('price') ?? 'Rp 199.000'
  const loginStatus = searchParams.get('login')
  const email = searchParams.get('email') ?? ''
  const userId = searchParams.get('user_id') ?? ''
  const [isPaying, setIsPaying] = useState(false)
  const [paymentError, setPaymentError] = useState<string | null>(null)
  const [paymentNotice, setPaymentNotice] = useState<string | null>(null)
  const [snapScriptUrl, setSnapScriptUrl] = useState<string | null>(null)

  const grossAmount = useMemo(() => {
    const digits = priceLabel.replace(/[^\d]/g, '')
    return Number.parseInt(digits || '0', 10)
  }, [priceLabel])

  useEffect(() => {
    if (!snapScriptUrl || !MIDTRANS_CLIENT_KEY) {
      return
    }

    const existing = document.getElementById('midtrans-snap-script')
    if (existing) {
      return
    }

    const script = document.createElement('script')
    script.id = 'midtrans-snap-script'
    script.src = snapScriptUrl
    script.setAttribute('data-client-key', MIDTRANS_CLIENT_KEY)
    script.async = true
    document.body.appendChild(script)

    return () => {
      script.remove()
    }
  }, [snapScriptUrl])

  const handlePayNow = async () => {
    if (!userId) {
      setPaymentError('User login belum ditemukan. Ulangi login Google terlebih dahulu.')
      return
    }

    if (!MIDTRANS_CLIENT_KEY) {
      setPaymentError('Midtrans client key untuk frontend belum tersedia.')
      return
    }

    try {
      setIsPaying(true)
      setPaymentError(null)
      setPaymentNotice(null)

      const response = await fetch(buildApiUrl('/payments/midtrans/create'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          plan: planSlug,
          price: grossAmount,
          email,
        }),
      })

      if (!response.ok) {
        const payload = (await response.json().catch(() => ({}))) as { detail?: string }
        throw new Error(payload.detail || 'Gagal membuat transaksi Midtrans.')
      }

      const payload = (await response.json()) as {
        payment_id: string
        snap_token: string
        redirect_url: string
      }

      const nextScriptUrl = payload.redirect_url.includes('sandbox')
        ? 'https://app.sandbox.midtrans.com/snap/snap.js'
        : 'https://app.midtrans.com/snap/snap.js'
      setSnapScriptUrl(nextScriptUrl)

      const payWithSnap = () => {
        if (!window.snap) {
          throw new Error('Snap Midtrans belum siap dimuat.')
        }

        window.snap.pay(payload.snap_token, {
          onSuccess: () => {
            window.location.href = `/payment/success?payment_id=${encodeURIComponent(payload.payment_id)}`
          },
          onPending: () => {
            window.location.href = `/payment/pending?payment_id=${encodeURIComponent(payload.payment_id)}`
          },
          onError: () => {
            window.location.href = `/payment/failed?payment_id=${encodeURIComponent(payload.payment_id)}`
          },
          onClose: () => {
            setPaymentNotice('Pembayaran belum diselesaikan. Kamu bisa lanjutkan lagi kapan pun dari halaman ini.')
          },
        })
      }

      if (window.snap) {
        payWithSnap()
        return
      }

      const start = window.setInterval(() => {
        if (window.snap) {
          window.clearInterval(start)
          payWithSnap()
        }
      }, 300)

      window.setTimeout(() => {
        window.clearInterval(start)
      }, 10000)
    } catch (error) {
      setPaymentError(error instanceof Error ? error.message : 'Terjadi kesalahan saat memulai pembayaran.')
    } finally {
      setIsPaying(false)
    }
  }

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
            <strong>{priceLabel}</strong>
            <span>Pembayaran satu kali</span>
          </div>

          <div className="payment-summary">
            <div className="payment-summary__row">
              <span>Paket</span>
              <strong>{planName}</strong>
            </div>
            <div className="payment-summary__row">
              <span>Tagihan</span>
              <strong>{priceLabel}</strong>
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

          <button
            type="button"
            className="btn btn-primary btn-large payment-panel__cta"
            onClick={() => void handlePayNow()}
            disabled={isPaying}
          >
            {isPaying ? 'Memulai pembayaran...' : 'Bayar Sekarang'}
          </button>

          {paymentError ? <p className="payment-panel__hint payment-panel__hint--error">{paymentError}</p> : null}
          {paymentNotice ? <p className="payment-panel__hint">{paymentNotice}</p> : null}
          {!paymentError && !paymentNotice ? (
            <p className="payment-panel__hint">Pembayaran akan dibuka melalui Midtrans Snap setelah transaksi dibuat.</p>
          ) : null}
        </div>
      </section>

      <section className="payment-note">
        <p>
          Status pembayaran belum disimpan sebagai transaksi final. Tahap berikutnya tinggal menyambungkan tombol bayar
          ke halaman selesai atau payment gateway asli.
        </p>
      </section>

      <SiteInfoFooter />
    </main>
  )
}
