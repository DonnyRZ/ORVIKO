'use client'

import type { Route } from 'next'
import Link from 'next/link'
import { useEffect, useMemo, useState } from 'react'
import { buildApiUrl } from '@/lib/api'

type SlideHistoryItem = {
  id: string
  title: string
  text_preview: string
  result_count: number
  embed_count: number
  updated_at: string
}

type ScriptHistoryItem = {
  id: string
  title: string
  task_preview: string
  selected_source: string
  current_step: 'task' | 'source' | 'observasi' | 'momen' | 'result'
  moment_count: number
  updated_at: string
}

type HistoryItem = {
  id: string
  kind: 'script' | 'slide'
  title: string
  summary: string
  meta: string
  updated_at: string
  href: Route
}

const formatDate = (value: string) => {
  if (!value) return '-'
  try {
    return new Intl.DateTimeFormat('id-ID', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(value))
  } catch {
    return value
  }
}

export function HistoryWorkspace() {
  const [scriptHistory, setScriptHistory] = useState<ScriptHistoryItem[]>([])
  const [slideHistory, setSlideHistory] = useState<SlideHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    const loadHistory = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const [scriptResponse, slideResponse] = await Promise.all([
          fetch(buildApiUrl('/script/history')),
          fetch(buildApiUrl('/slides/history')),
        ])

        if (!scriptResponse.ok || !slideResponse.ok) {
          throw new Error('Gagal memuat histori.')
        }

        const scriptData = (await scriptResponse.json()) as { history?: ScriptHistoryItem[] }
        const slideData = (await slideResponse.json()) as { history?: SlideHistoryItem[] }
        if (!active) return

        setScriptHistory(Array.isArray(scriptData.history) ? scriptData.history : [])
        setSlideHistory(Array.isArray(slideData.history) ? slideData.history : [])
      } catch (err) {
        if (!active) return
        setError(err instanceof Error ? err.message : 'Gagal memuat histori.')
      } finally {
        if (active) {
          setIsLoading(false)
        }
      }
    }

    void loadHistory()

    return () => {
      active = false
    }
  }, [])

  const historyItems = useMemo<HistoryItem[]>(() => {
    const scripts = scriptHistory.map((item) => ({
      id: `script-${item.id}`,
      kind: 'script' as const,
      title: item.title,
      summary: item.task_preview || item.selected_source || 'Draft script tanpa ringkasan.',
      meta: `${item.current_step} - ${item.moment_count} momen`,
      updated_at: item.updated_at,
      href: `/script?workspace_id=${item.id}` as Route,
    }))

    const slides = slideHistory.map((item) => ({
      id: `slide-${item.id}`,
      kind: 'slide' as const,
      title: item.title,
      summary: item.text_preview || 'Postingan gambar tanpa ringkasan teks.',
      meta: `${item.result_count} result - ${item.embed_count} embed`,
      updated_at: item.updated_at,
      href: `/slides?slide_id=${item.id}` as Route,
    }))

    return [...scripts, ...slides].sort((a, b) => b.updated_at.localeCompare(a.updated_at))
  }, [scriptHistory, slideHistory])

  return (
    <main className="history-page">
      <header className="history-page__header">
        <div>
          <p className="section-eyebrow">Histori</p>
          <h1 className="history-page__title display-font">Histori Project</h1>
        </div>
        <Link href={'/home' as Route} className="btn btn-ghost">
          Kembali ke dashboard
        </Link>
      </header>

      <section className="history-page__content">
        {error ? <p className="dashboard-error">{error}</p> : null}
        {isLoading ? (
          <p className="dashboard-empty">Memuat histori...</p>
        ) : historyItems.length ? (
          <div className="history-page__list">
            {historyItems.map((item) => (
              <Link key={item.id} href={item.href} className="history-page__item">
                <div>
                  <span className="dashboard-history-card__type">{item.kind === 'script' ? 'Script' : 'Gambar'}</span>
                  <h2>{item.title}</h2>
                  <p>{item.summary}</p>
                </div>
                <div className="history-page__meta">
                  <span>{item.meta}</span>
                  <time>{formatDate(item.updated_at)}</time>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <p className="dashboard-empty">Belum ada histori project.</p>
        )}
      </section>
    </main>
  )
}
