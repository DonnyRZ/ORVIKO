import { Suspense } from 'react'
import { ScriptWorkspaceShell } from '@/features/script/ScriptWorkspaceShell'

export default function ScriptPage() {
  return (
    <Suspense fallback={null}>
      <ScriptWorkspaceShell />
    </Suspense>
  )
}
