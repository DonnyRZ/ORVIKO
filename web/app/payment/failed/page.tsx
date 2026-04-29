import { Suspense } from 'react'
import { PaymentStatusPage } from '@/features/payment/PaymentStatusPage'

export default function PaymentFailedPage() {
  return (
    <Suspense fallback={null}>
      <PaymentStatusPage tone="failed" />
    </Suspense>
  )
}
