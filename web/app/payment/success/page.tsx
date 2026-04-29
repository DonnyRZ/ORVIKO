import { Suspense } from 'react'
import { PaymentStatusPage } from '@/features/payment/PaymentStatusPage'

export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={null}>
      <PaymentStatusPage tone="success" />
    </Suspense>
  )
}
