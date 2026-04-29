'use client'

import type { Route } from 'next'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { buildApiUrl } from '@/lib/api'

type ScriptStep = 'task' | 'source' | 'observasi' | 'momen' | 'result'

type ScriptSourceOption = {
  title: string
  text: string
}

type ScriptObservations = {
  perilaku: string[]
  emosi: string[]
  situasi: string[]
}

type ScriptKnowledgeBaseSummary = {
  id: string
  title: string
  creator: string
  audience: string
  source_patterns: string[]
  moment_patterns: string[]
  sample_tasks: string[]
}

type ScriptWorkspace = {
  id: string
  title: string
  knowledge_base_id: string
  current_step: ScriptStep
  active_profile_id: string
  task: string
  selected_source: string
  source_options: ScriptSourceOption[]
  observations: ScriptObservations
  moments: string[]
  observation_variant_index: number
  moment_variant_index: number
  created_at: string
  updated_at: string
}

type ScriptWorkspaceResponse = {
  workspace: ScriptWorkspace
  knowledge_base: ScriptKnowledgeBaseSummary
}

const emptyObservations: ScriptObservations = {
  perilaku: [],
  emosi: [],
  situasi: [],
}

const emptyWorkspace: ScriptWorkspace = {
  id: '',
  title: 'Draft script aktif',
  knowledge_base_id: '',
  current_step: 'task',
  active_profile_id: '',
  task: '',
  selected_source: '',
  source_options: [],
  observations: emptyObservations,
  moments: [],
  observation_variant_index: 0,
  moment_variant_index: 0,
  created_at: '',
  updated_at: '',
}

const emptyKnowledgeBase: ScriptKnowledgeBaseSummary = {
  id: '',
  title: 'Knowledge base',
  creator: '',
  audience: '',
  source_patterns: [],
  moment_patterns: [],
  sample_tasks: [],
}

const steps: Array<{ id: Exclude<ScriptStep, 'result'>; title: string; copy: string }> = [
  { id: 'task', title: 'Task', copy: 'User memberi arahan awal yang akan dibaca agent.' },
  { id: 'source', title: 'Source', copy: 'Agent menyiapkan shortlist source, lalu user memilih arahnya.' },
  { id: 'observasi', title: 'Observasi', copy: 'Perilaku, emosi, dan situasi dibentuk dari source yang dipilih.' },
  { id: 'momen', title: 'Momen', copy: 'Agent menyusun scene terurut yang bisa langsung diedit user.' },
]

const normalizeObservations = (value: Partial<ScriptObservations> | undefined): ScriptObservations => ({
  perilaku: Array.isArray(value?.perilaku) ? value!.perilaku : [],
  emosi: Array.isArray(value?.emosi) ? value!.emosi : [],
  situasi: Array.isArray(value?.situasi) ? value!.situasi : [],
})

const normalizeWorkspace = (workspace: Partial<ScriptWorkspace> | undefined): ScriptWorkspace => ({
  id: workspace?.id ?? '',
  title: workspace?.title ?? 'Draft script aktif',
  knowledge_base_id: workspace?.knowledge_base_id ?? '',
  current_step:
    workspace?.current_step === 'source' ||
    workspace?.current_step === 'observasi' ||
    workspace?.current_step === 'momen' ||
    workspace?.current_step === 'result'
      ? workspace.current_step
      : 'task',
  active_profile_id: workspace?.active_profile_id ?? '',
  task: workspace?.task ?? '',
  selected_source: workspace?.selected_source ?? '',
  source_options: Array.isArray(workspace?.source_options) ? workspace!.source_options : [],
  observations: normalizeObservations(workspace?.observations),
  moments: Array.isArray(workspace?.moments) ? workspace!.moments : [],
  observation_variant_index: typeof workspace?.observation_variant_index === 'number' ? workspace.observation_variant_index : 0,
  moment_variant_index: typeof workspace?.moment_variant_index === 'number' ? workspace.moment_variant_index : 0,
  created_at: workspace?.created_at ?? '',
  updated_at: workspace?.updated_at ?? '',
})

const normalizeKnowledgeBase = (
  knowledgeBase: Partial<ScriptKnowledgeBaseSummary> | undefined
): ScriptKnowledgeBaseSummary => ({
  id: knowledgeBase?.id ?? '',
  title: knowledgeBase?.title ?? 'Knowledge base',
  creator: knowledgeBase?.creator ?? '',
  audience: knowledgeBase?.audience ?? '',
  source_patterns: Array.isArray(knowledgeBase?.source_patterns) ? knowledgeBase!.source_patterns : [],
  moment_patterns: Array.isArray(knowledgeBase?.moment_patterns) ? knowledgeBase!.moment_patterns : [],
  sample_tasks: Array.isArray(knowledgeBase?.sample_tasks) ? knowledgeBase!.sample_tasks : [],
})

const hasObservations = (observations: ScriptObservations) =>
  observations.perilaku.length > 0 || observations.emosi.length > 0 || observations.situasi.length > 0

const stepLabel = (step: ScriptStep) =>
  step === 'result' ? 'Result' : steps.find((item) => item.id === step)?.title ?? 'Task'

export function ScriptWorkspaceShell() {
  const searchParams = useSearchParams()
  const workspaceId = searchParams.get('workspace_id') ?? ''
  const [workspace, setWorkspace] = useState<ScriptWorkspace>(emptyWorkspace)
  const [knowledgeBase, setKnowledgeBase] = useState<ScriptKnowledgeBaseSummary>(emptyKnowledgeBase)
  const [isLoading, setIsLoading] = useState(true)
  const [isActing, setIsActing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [agentStatus, setAgentStatus] = useState('Memuat workspace script...')

  const sourceVisible =
    workspace.source_options.length > 0 || workspace.selected_source.trim().length > 0 || workspace.current_step !== 'task'
  const observationsVisible = sourceVisible || hasObservations(workspace.observations)
  const momentsVisible = workspace.moments.length > 0 || workspace.current_step === 'momen' || workspace.current_step === 'result'
  const completed = {
    task: workspace.task.trim().length > 0,
    source: workspace.selected_source.trim().length > 0,
    observasi: hasObservations(workspace.observations),
    momen: workspace.moments.length > 0,
  }

  const applyResponse = (payload: ScriptWorkspaceResponse) => {
    setWorkspace(normalizeWorkspace(payload.workspace))
    setKnowledgeBase(normalizeKnowledgeBase(payload.knowledge_base))
  }

  const requestJson = async <T,>(path: string, options?: RequestInit): Promise<T> => {
    const response = await fetch(buildApiUrl(path), {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers ?? {}),
      },
    })

    if (!response.ok) {
      let message = 'Terjadi kesalahan pada workspace script.'
      try {
        const data = (await response.json()) as { detail?: string }
        message = data.detail || message
      } catch {
        const text = await response.text()
        message = text || message
      }
      throw new Error(message)
    }

    return (await response.json()) as T
  }

  const workspacePath = (suffix = '') =>
    workspaceId ? `/script/workspaces/${workspaceId}${suffix}` : `/script/workspace${suffix}`

  const loadWorkspace = async () => {
    const payload = await requestJson<ScriptWorkspaceResponse>(
      workspaceId ? `/script/workspaces/${workspaceId}` : '/script/workspace'
    )
    applyResponse(payload)
    setAgentStatus('Workspace script siap. Mulai dari task, lalu agent akan membuka flow source sampai momen.')
  }

  useEffect(() => {
    let active = true

    const bootstrap = async () => {
      try {
        setIsLoading(true)
        setError(null)
        await loadWorkspace()
      } catch (err) {
        if (!active) return
        setError(err instanceof Error ? err.message : 'Gagal memuat workspace script.')
        setAgentStatus('Workspace script gagal dimuat.')
      } finally {
        if (active) {
          setIsLoading(false)
        }
      }
    }

    void bootstrap()

    return () => {
      active = false
    }
  }, [workspaceId])

  const runAction = async (status: string, work: () => Promise<void>, nextStatus: string) => {
    try {
      setIsActing(true)
      setError(null)
      setAgentStatus(status)
      await work()
      setAgentStatus(nextStatus)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Terjadi kesalahan saat memproses workspace script.'
      setError(message)
      setAgentStatus(message)
    } finally {
      setIsActing(false)
    }
  }

  const handleTaskChange = (value: string) => {
    setWorkspace((prev) => ({
      ...prev,
      task: value,
    }))
  }

  const handleSelectSampleTask = (task: string) => {
    setWorkspace((prev) => ({
      ...prev,
      task,
    }))
  }

  const handleStart = async () => {
    if (!workspace.task.trim()) {
      setError('Task wajib diisi sebelum memulai flow asisten.')
      setAgentStatus('Isi task dulu supaya agent punya arah kerja yang jelas.')
      return
    }

    await runAction(
      'Agent sedang membaca knowledge base dan menyiapkan shortlist source...',
      async () => {
        await requestJson<ScriptWorkspaceResponse>(workspacePath('/task'), {
          method: 'PATCH',
          body: JSON.stringify({ task: workspace.task }),
        })
        const payload = await requestJson<ScriptWorkspaceResponse>(workspacePath('/source-options'), {
          method: 'POST',
          body: JSON.stringify({}),
        })
        applyResponse(payload)
      },
      'Agent sudah menyiapkan shortlist source. Pilih atau edit dulu sebelum masuk ke observasi.'
    )
  }

  const handleReset = async () => {
    await runAction(
      'Workspace script sedang direset ke kondisi awal...',
      async () => {
        const payload = await requestJson<ScriptWorkspaceResponse>(workspacePath('/reset'), {
          method: 'POST',
          body: JSON.stringify({}),
        })
        applyResponse(payload)
      },
      'Flow sudah direset. Kamu bisa mulai lagi dari task baru.'
    )
  }

  const handleSelectSourceOption = (option: ScriptSourceOption) => {
    setWorkspace((prev) => ({
      ...prev,
      current_step: 'source',
      selected_source: option.text,
    }))
  }

  const handleSourceChange = (value: string) => {
    setWorkspace((prev) => ({
      ...prev,
      current_step: 'source',
      selected_source: value,
    }))
  }

  const persistSource = async () => {
    const payload = await requestJson<ScriptWorkspaceResponse>(workspacePath('/source'), {
      method: 'PATCH',
      body: JSON.stringify({ selected_source: workspace.selected_source }),
    })
    applyResponse(payload)
  }

  const handleContinueFromSource = async () => {
    if (!workspace.selected_source.trim()) {
      setError('Source tidak boleh kosong.')
      setAgentStatus('Pilih atau isi source dulu sebelum lanjut.')
      return
    }

    await runAction(
      'Agent sedang menyusun perilaku, emosi, dan situasi dari source yang dipilih...',
      async () => {
        await persistSource()
        const payload = await requestJson<ScriptWorkspaceResponse>(workspacePath('/observations/generate'), {
          method: 'POST',
          body: JSON.stringify({ regenerate: false }),
        })
        applyResponse(payload)
      },
      'Observasi sudah siap. Review dulu sebelum agent masuk ke tahap momen.'
    )
  }

  const handleRegenerateObservations = async () => {
    if (!workspace.selected_source.trim()) {
      setError('Source wajib dipilih sebelum generate ulang observasi.')
      return
    }

    await runAction(
      'Agent sedang menyusun ulang observasi berdasarkan source yang aktif...',
      async () => {
        await persistSource()
        const payload = await requestJson<ScriptWorkspaceResponse>(workspacePath('/observations/generate'), {
          method: 'POST',
          body: JSON.stringify({ regenerate: true }),
        })
        applyResponse(payload)
      },
      'Observasi versi baru sudah siap. Kamu bisa edit lagi sebelum lanjut ke momen.'
    )
  }

  const handleObservationChange = (group: keyof ScriptObservations, index: number, value: string) => {
    setWorkspace((prev) => {
      const nextGroup = [...prev.observations[group]]
      nextGroup[index] = value
      return {
        ...prev,
        current_step: 'observasi',
        observations: {
          ...prev.observations,
          [group]: nextGroup,
        },
      }
    })
  }

  const persistObservations = async () => {
    const payload = await requestJson<ScriptWorkspaceResponse>(workspacePath('/observations'), {
      method: 'PATCH',
      body: JSON.stringify(workspace.observations),
    })
    applyResponse(payload)
  }

  const handleContinueToMoments = async () => {
    if (!hasObservations(workspace.observations)) {
      setError('Observasi wajib ada sebelum generate momen.')
      return
    }

    await runAction(
      'Agent sedang menyusun rekomendasi momen dari observasi yang sudah disepakati...',
      async () => {
        await persistObservations()
        const payload = await requestJson<ScriptWorkspaceResponse>(workspacePath('/moments/generate'), {
          method: 'POST',
          body: JSON.stringify({ regenerate: false }),
        })
        applyResponse(payload)
      },
      'Momen sudah siap. Edit urutan scene sampai terasa cukup dekat ke video yang ingin dibangun.'
    )
  }

  const handleRegenerateMoments = async () => {
    if (!hasObservations(workspace.observations)) {
      setError('Observasi wajib ada sebelum generate ulang momen.')
      return
    }

    await runAction(
      'Agent sedang menyusun ulang momen berdasarkan observasi terbaru...',
      async () => {
        await persistObservations()
        const payload = await requestJson<ScriptWorkspaceResponse>(workspacePath('/moments/generate'), {
          method: 'POST',
          body: JSON.stringify({ regenerate: true }),
        })
        applyResponse(payload)
      },
      'Momen versi baru sudah siap. Lanjutkan edit scene jika masih perlu.'
    )
  }

  const handleMomentChange = (index: number, value: string) => {
    setWorkspace((prev) => {
      const nextMoments = [...prev.moments]
      nextMoments[index] = value
      return {
        ...prev,
        current_step: 'momen',
        moments: nextMoments,
      }
    })
  }

  const handleMoveMoment = (index: number, direction: 'up' | 'down') => {
    setWorkspace((prev) => {
      const nextMoments = [...prev.moments]
      const targetIndex = direction === 'up' ? index - 1 : index + 1
      if (targetIndex < 0 || targetIndex >= nextMoments.length) {
        return prev
      }
      ;[nextMoments[index], nextMoments[targetIndex]] = [nextMoments[targetIndex], nextMoments[index]]
      return {
        ...prev,
        current_step: 'momen',
        moments: nextMoments,
      }
    })
  }

  const handleDeleteMoment = (index: number) => {
    setWorkspace((prev) => ({
      ...prev,
      current_step: 'momen',
      moments: prev.moments.filter((_, itemIndex) => itemIndex !== index),
    }))
  }

  const handleAddMoment = () => {
    setWorkspace((prev) => ({
      ...prev,
      current_step: 'momen',
      moments: [...prev.moments, 'Scene baru: tambahkan momen yang ingin kamu masukkan ke alur video.'],
    }))
  }

  const handleSaveMoments = async () => {
    if (!workspace.moments.length) {
      setError('Minimal satu momen harus tersedia sebelum disimpan.')
      return
    }

    await runAction(
      'Menyimpan momen final ke draft script aktif...',
      async () => {
        const payload = await requestJson<ScriptWorkspaceResponse>(workspacePath('/moments'), {
          method: 'PATCH',
          body: JSON.stringify({ moments: workspace.moments, current_step: 'result' }),
        })
        applyResponse(payload)
      },
      'Draft script aktif sudah tersimpan. Kamu masih bisa kembali mengubah momen kapan pun diperlukan.'
    )
  }

  const handleUnlockMoments = () => {
    setWorkspace((prev) => ({
      ...prev,
      current_step: 'momen',
    }))
    setAgentStatus('Kamu kembali ke tahap momen untuk melanjutkan revisi scene.')
  }

  return (
    <main className="workspace-shell">
      <header className="workspace-header">
        <div className="brand">
          <div className="brand-mark">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/branding/logo-orviko.png" alt="Logo ORVIKO" className="brand-mark__image" />
          </div>
          <div className="brand-copy">
            <p className="brand-title display-font">ORVIKO Script</p>
            <p className="brand-subtitle">Workspace asisten dari task sampai momen</p>
          </div>
          <span className="tag tag-accent">Mode asisten</span>
        </div>
        <div className="header-actions">
          <Link href={'/home' as Route} className="btn btn-ghost">
            Kembali ke home
          </Link>
          <Link href={'/slides' as Route} className="btn">
            Buka slides
          </Link>
        </div>
      </header>

      <section className="workspace-grid workspace-grid--script">
        <aside className="workspace-column workspace-column--scroll">
          <section className="column-section">
            <div className="section-header">
              <div>
                <p className="section-eyebrow">Task</p>
                <h2 className="section-title display-font">Mulai dari arahan user</h2>
                <p className="section-subtitle">Isi task singkat, lalu agent akan menyiapkan shortlist source.</p>
              </div>
            </div>

            <div className="field">
              <label className="field__label" htmlFor="script-task-input">
                Task / query
              </label>
              <textarea
                id="script-task-input"
                className="field__input field__input--area"
                rows={5}
                value={workspace.task}
                onChange={(event) => handleTaskChange(event.target.value)}
                placeholder="Contoh: aku mau bahas kreator yang views-nya stuck padahal dia merasa kontennya sudah niat."
              />
              <p className="field__hint">Task ini menjadi pintu masuk awal sebelum agent membaca context dari knowledge base.</p>
            </div>

            {knowledgeBase.sample_tasks.length ? (
              <div className="field">
                <p className="field__label">Contoh task cepat</p>
                <div className="preset-row">
                  {knowledgeBase.sample_tasks.map((task) => (
                    <button
                      key={task}
                      className={`preset-chip ${workspace.task === task ? 'is-active' : ''}`}
                      type="button"
                      onClick={() => handleSelectSampleTask(task)}
                    >
                      {task}
                    </button>
                  ))}
                </div>
              </div>
            ) : null}

            <div className="surface-actions">
              <button className="btn btn-primary" type="button" onClick={handleStart} disabled={isLoading || isActing}>
                {isActing ? 'Memproses...' : 'Mulai'}
              </button>
              <button className="btn btn-ghost" type="button" onClick={handleReset} disabled={isLoading || isActing}>
                Reset
              </button>
            </div>
            {error ? <p className="field__hint">{error}</p> : null}
          </section>

          {sourceVisible ? (
            <section className="column-section">
              <div className="section-header">
                <div>
                  <p className="section-eyebrow">Source</p>
                  <h2 className="section-title display-font">Pilih atau edit source</h2>
                  <p className="section-subtitle">User tetap pegang kontrol sebelum agent masuk ke observasi.</p>
                </div>
              </div>

              <div className="field">
                <label className="field__label" htmlFor="script-source-input">
                  Source terpilih
                </label>
                <textarea
                  id="script-source-input"
                  className="field__input field__input--area"
                  rows={4}
                  value={workspace.selected_source}
                  onChange={(event) => handleSourceChange(event.target.value)}
                  placeholder="Source pilihan akan tampil di sini."
                />
              </div>

              <div className="surface-actions">
                <button className="btn btn-primary" type="button" onClick={handleContinueFromSource} disabled={isLoading || isActing}>
                  Lanjutkan
                </button>
              </div>
            </section>
          ) : null}

          {observationsVisible ? (
            <section className="column-section">
              <div className="section-header">
                <div>
                  <p className="section-eyebrow">Observasi</p>
                  <h2 className="section-title display-font">Review sebelum jadi momen</h2>
                  <p className="section-subtitle">Perilaku, emosi, dan situasi bisa diedit atau di-generate ulang.</p>
                </div>
              </div>

              <div className="surface-actions">
                <button className="btn btn-ghost" type="button" onClick={handleRegenerateObservations} disabled={isLoading || isActing}>
                  Generate ulang
                </button>
                <button className="btn btn-primary" type="button" onClick={handleContinueToMoments} disabled={isLoading || isActing}>
                  Lanjut ke momen
                </button>
              </div>
            </section>
          ) : null}

          {momentsVisible ? (
            <section className="column-section">
              <div className="section-header">
                <div>
                  <p className="section-eyebrow">Momen</p>
                  <h2 className="section-title display-font">Finalisasi scene</h2>
                  <p className="section-subtitle">Edit urutan momen sampai terasa cukup dekat ke video yang ingin dibangun.</p>
                </div>
              </div>

              <div className="surface-actions">
                <button className="btn btn-ghost" type="button" onClick={handleRegenerateMoments} disabled={isLoading || isActing}>
                  Generate ulang
                </button>
                <button className="btn" type="button" onClick={handleAddMoment} disabled={isLoading || isActing}>
                  Tambah scene
                </button>
                <button className="btn btn-primary" type="button" onClick={handleSaveMoments} disabled={isLoading || isActing}>
                  Simpan hasil
                </button>
              </div>
            </section>
          ) : null}
        </aside>

        <section className="workspace-column workspace-column--scroll">
          <div className="stage-stack">
            <section className="agent-banner">
              <div className="section-header">
                <div>
                  <p className="section-eyebrow">Agent</p>
                  <h2 className="section-title display-font">Status agent</h2>
                </div>
                <span className="tag">{stepLabel(workspace.current_step)}</span>
              </div>
              <div className="agent-status">
                <span className="agent-dot"></span>
                <span>{isLoading ? 'Memuat workspace script...' : agentStatus}</span>
              </div>
            </section>

            <section className="surface">
              <div className="surface-header">
                <div>
                  <p className="section-eyebrow">Task</p>
                  <h2 className="section-title display-font">Task aktif</h2>
                </div>
              </div>
              <div className="surface-content">
                {workspace.task.trim() ? (
                  <div className="locked-item">
                    <strong>Task</strong>
                    <p>{workspace.task}</p>
                  </div>
                ) : (
                  <div className="stage-empty">Belum ada task aktif. Isi task di panel kiri lalu klik <strong>Mulai</strong>.</div>
                )}
              </div>
            </section>

            <section className="surface">
              <div className="surface-header">
                <div>
                  <p className="section-eyebrow">Source</p>
                  <h2 className="section-title display-font">Shortlist source</h2>
                </div>
              </div>
              <div className="surface-content">
                {workspace.source_options.length ? (
                  <>
                    <div className="source-grid">
                      {workspace.source_options.map((option) => (
                        <button
                          key={option.text}
                          type="button"
                          className={`source-card ${workspace.selected_source === option.text ? 'is-selected' : ''}`}
                          onClick={() => handleSelectSourceOption(option)}
                        >
                          <strong>{option.title}</strong>
                          <p>{option.text}</p>
                        </button>
                      ))}
                    </div>
                    <div className="result-chip">
                      Agent menampilkan shortlist source yang sudah dipilih dari knowledge base. User bisa klik salah satu
                      lalu mengubah wording-nya di panel kiri.
                    </div>
                  </>
                ) : (
                  <div className="stage-empty">Source shortlist akan muncul setelah agent membaca task.</div>
                )}
              </div>
            </section>

            <section className="surface">
              <div className="surface-header">
                <div>
                  <p className="section-eyebrow">Observasi</p>
                  <h2 className="section-title display-font">Perilaku, emosi, situasi</h2>
                </div>
              </div>
              <div className="surface-content">
                {hasObservations(workspace.observations) ? (
                  <div className="obs-grid">
                    {([
                      { key: 'perilaku', title: 'Perilaku' },
                      { key: 'emosi', title: 'Emosi' },
                      { key: 'situasi', title: 'Situasi' },
                    ] as const).map((group) => (
                      <section key={group.key} className="obs-group">
                        <div className="section-header">
                          <div>
                            <p className="section-eyebrow">{group.title}</p>
                            <h3 className="section-title">{group.title} hasil agent</h3>
                          </div>
                        </div>
                        <div className="obs-list">
                          {workspace.observations[group.key].map((value, index) => (
                            <div key={`${group.key}-${index}`} className="obs-item">
                              <textarea
                                value={value}
                                onChange={(event) => handleObservationChange(group.key, index, event.target.value)}
                              />
                            </div>
                          ))}
                        </div>
                      </section>
                    ))}
                  </div>
                ) : (
                  <div className="stage-empty">Observasi akan muncul setelah source dikunci.</div>
                )}
              </div>
            </section>

            <section className="surface">
              <div className="surface-header">
                <div>
                  <p className="section-eyebrow">Momen</p>
                  <h2 className="section-title display-font">Scene terurut</h2>
                </div>
              </div>
              <div className="surface-content">
                {workspace.moments.length ? (
                  <div className="moment-list">
                    {workspace.moments.map((moment, index) => (
                      <div key={`moment-${index}`} className="moment-item">
                        <div className="moment-meta">
                          <span className="moment-index">Scene {index + 1}</span>
                          <div className="moment-actions">
                            <button className="btn btn-small" type="button" onClick={() => handleMoveMoment(index, 'up')}>
                              Naik
                            </button>
                            <button className="btn btn-small" type="button" onClick={() => handleMoveMoment(index, 'down')}>
                              Turun
                            </button>
                            <button className="btn btn-small btn-ghost" type="button" onClick={() => handleDeleteMoment(index)}>
                              Hapus
                            </button>
                          </div>
                        </div>
                        <textarea value={moment} onChange={(event) => handleMomentChange(index, event.target.value)} />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="stage-empty">Momen akan muncul setelah observasi disepakati.</div>
                )}
              </div>
            </section>
          </div>
        </section>

        <aside className="workspace-column workspace-column--scroll workspace-column--right">
          <section className="column-section">
            <div className="section-header">
              <div>
                <p className="section-eyebrow">Knowledge base</p>
                <h2 className="section-title display-font">{knowledgeBase.title || 'Knowledge base aktif'}</h2>
                <p className="section-subtitle">Knowledge base ini menjadi fondasi runtime untuk source, observasi, dan momen.</p>
              </div>
            </div>

            <div className="sidebar-list">
              <div className="sidebar-item">
                <strong>Creator profile</strong>
                <p>{knowledgeBase.creator || 'Belum ada ringkasan creator profile.'}</p>
              </div>
              <div className="sidebar-item">
                <strong>Audience</strong>
                <p>{knowledgeBase.audience || 'Belum ada ringkasan audience.'}</p>
              </div>
              <div className="sidebar-item">
                <strong>Source patterns</strong>
                <ul>
                  {knowledgeBase.source_patterns.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <div className="sidebar-item">
                <strong>Moment patterns</strong>
                <ul>
                  {knowledgeBase.moment_patterns.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </section>

          <section className="column-section">
            <div className="section-header">
              <div>
                <p className="section-eyebrow">Progress</p>
                <h2 className="section-title display-font">Tahap kerja</h2>
              </div>
            </div>

            <div className="step-list">
              {steps.map((step, index) => {
                const isDone = completed[step.id]
                const isActive = workspace.current_step === step.id || (workspace.current_step === 'result' && step.id === 'momen')
                return (
                  <div key={step.id} className={`step-item ${isActive ? 'is-active' : ''} ${isDone ? 'is-done' : ''}`}>
                    <div className="step-index">{isDone ? '✓' : index + 1}</div>
                    <div>
                      <p className="step-name">{step.title}</p>
                      <p className="step-copy">{step.copy}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </section>

          <section className="column-section">
            <div className="section-header">
              <div>
                <p className="section-eyebrow">Draft aktif</p>
                <h2 className="section-title display-font">Ringkasan hasil</h2>
                <p className="section-subtitle">
                  {workspace.current_step === 'result'
                    ? 'Draft aktif sudah tersimpan. Kamu tetap bisa membuka lagi tahap momen untuk revisi.'
                    : 'Ringkasan ini mengikuti state draft script aktif yang sedang kamu kerjakan.'}
                </p>
              </div>
            </div>

            <div className="result-block">
              {workspace.task.trim() ? (
                <div className="locked-item">
                  <strong>Task</strong>
                  <p>{workspace.task}</p>
                </div>
              ) : null}

              {workspace.selected_source.trim() ? (
                <div className="locked-item">
                  <strong>Source</strong>
                  <p>{workspace.selected_source}</p>
                </div>
              ) : null}

              {hasObservations(workspace.observations) ? (
                <div className="locked-item">
                  <strong>Observasi</strong>
                  <ul>
                    {workspace.observations.perilaku.map((item, index) => (
                      <li key={`p-${index}`}>{item}</li>
                    ))}
                    {workspace.observations.emosi.map((item, index) => (
                      <li key={`e-${index}`}>{item}</li>
                    ))}
                    {workspace.observations.situasi.map((item, index) => (
                      <li key={`s-${index}`}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {workspace.moments.length ? (
                <div className="locked-item">
                  <strong>Momen</strong>
                  <ul>
                    {workspace.moments.map((item, index) => (
                      <li key={`m-${index}`}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <div className="result-chip">Belum ada momen yang tersimpan di draft aktif.</div>
              )}

              {workspace.current_step === 'result' ? (
                <div className="surface-actions">
                  <button className="btn btn-ghost" type="button" onClick={handleUnlockMoments} disabled={isLoading || isActing}>
                    Ubah momen lagi
                  </button>
                </div>
              ) : null}
            </div>
          </section>
        </aside>
      </section>
    </main>
  )
}
