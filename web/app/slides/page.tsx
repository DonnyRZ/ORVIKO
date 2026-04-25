import { Suspense } from 'react'
import { SlidesWorkspace } from '@/features/slides/SlidesWorkspace'

export default function SlidesPage() {
  return (
    <Suspense fallback={null}>
      <SlidesWorkspace />
    </Suspense>
  )
}
