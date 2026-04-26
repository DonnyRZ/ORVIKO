import { Suspense } from 'react'
import { PaymentPage } from '@/features/payment/PaymentPage'

export default function PaymentRoutePage() {
  return (
    <Suspense fallback={null}>
      <PaymentPage />
    </Suspense>
  )
}
