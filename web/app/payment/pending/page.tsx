import { Suspense } from 'react'
import { PaymentStatusPage } from '@/features/payment/PaymentStatusPage'

export default function PaymentPendingPage() {
  return (
    <Suspense fallback={null}>
      <PaymentStatusPage tone="pending" />
    </Suspense>
  )
}
