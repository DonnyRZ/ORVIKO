'use client'

import { useEffect, useState } from 'react'
import type { Route } from 'next'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { buildApiUrl } from '@/lib/api'

type StatusTone = 'success' | 'pending' | 'failed'

const copyMap: Record<StatusTone, { label: string; title: string; body: string }> = {
  success: {
    label: 'Pembayaran Berhasil',
    title: 'Pembayaran berhasil diproses.',
    body: 'Status final tetap akan mengikuti konfirmasi dari sistem ORVIKO dan webhook Midtrans.',
  },
  pending: {
    label: 'Menunggu Pembayaran',
    title: 'Transaksi kamu masih menunggu penyelesaian.',
    body: 'Kamu bisa menyelesaikan pembayaran dari channel yang dipilih atau cek kembali statusnya nanti.',
  },
  failed: {
    label: 'Pembayaran Gagal',
    title: 'Pembayaran belum berhasil diproses.',
    body: 'Silakan coba lagi dari halaman payment atau gunakan metode pembayaran lain jika tersedia.',
  },
}

export function PaymentStatusPage({ tone }: { tone: StatusTone }) {
  const searchParams = useSearchParams()
  const paymentId = searchParams.get('payment_id') ?? ''
  const [status, setStatus] = useState<string>('')
  const [orderId, setOrderId] = useState<string>('')
  const [plan, setPlan] = useState<string>('')
  const [amount, setAmount] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!paymentId) {
      setError('Payment ID tidak ditemukan.')
      return
    }

    let active = true
    const loadStatus = async () => {
      try {
        const response = await fetch(buildApiUrl(`/payments/${paymentId}`))
        if (!response.ok) {
          throw new Error('Gagal memuat status payment.')
        }
        const payload = (await response.json()) as {
          status: string
          order_id: string
          plan: string
          gross_amount: number
        }
        if (!active) return
        setStatus(payload.status)
        setOrderId(payload.order_id)
        setPlan(payload.plan)
        setAmount(payload.gross_amount)
      } catch (err) {
        if (!active) return
        setError(err instanceof Error ? err.message : 'Gagal memuat status payment.')
      }
    }

    void loadStatus()
    return () => {
      active = false
    }
  }, [paymentId])

  const copy = copyMap[tone]
  const amountLabel = amount ? `Rp ${amount.toLocaleString('id-ID')}` : '-'

  return (
    <main className="legal-page">
      <header className="legal-header">
        <Link href={'/' as Route} className="landing-brand">
          <img src="/branding/logo-orviko.png" alt="Logo ORVIKO" className="landing-brand__mark" />
          <div>
            <strong className="display-font">ORVIKO</strong>
            <span>{copy.label}</span>
          </div>
        </Link>

        <div className="legal-header__actions">
          <Link href={'/payment' as Route} className="btn btn-ghost">
            Kembali ke payment
          </Link>
        </div>
      </header>

      <section className="legal-hero">
        <p className="landing-kicker">{copy.label}</p>
        <h1 className="landing-title display-font">{copy.title}</h1>
        <p className="landing-subtitle">{copy.body}</p>
      </section>

      <section className="legal-sections">
        <article className="legal-card">
          <h2 className="display-font">Ringkasan Transaksi</h2>
          {error ? (
            <p>{error}</p>
          ) : (
            <>
              <p>Order ID: {orderId || '-'}</p>
              <p>Paket: {plan || '-'}</p>
              <p>Tagihan: {amountLabel}</p>
              <p>Status terakhir: {status || '-'}</p>
            </>
          )}
        </article>
      </section>
    </main>
  )
}
