'use client'

import type { Route } from 'next'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
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

type DashboardHistoryItem = {
  id: string
  kind: 'script' | 'slide'
  title: string
  summary: string
  updated_at: string
  href: Route
}

const formatDate = (value: string) => {
  if (!value) return '-'
  try {
    return new Intl.DateTimeFormat('id-ID', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(value))
  } catch {
    return value
  }
}

function Icon({ name }: { name: 'dashboard' | 'workspace' | 'history' | 'settings' | 'script' | 'image' | 'menu' }) {
  const common = {
    width: 22,
    height: 22,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.8,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    'aria-hidden': true,
  }

  if (name === 'dashboard') {
    return (
      <svg {...common}>
        <rect x="3" y="3" width="7" height="7" />
        <rect x="14" y="3" width="7" height="7" />
        <rect x="3" y="14" width="7" height="7" />
        <rect x="14" y="14" width="7" height="7" />
      </svg>
    )
  }

  if (name === 'workspace') {
    return (
      <svg {...common}>
        <path d="M4 6h16" />
        <path d="M4 12h16" />
        <path d="M4 18h10" />
      </svg>
    )
  }

  if (name === 'history') {
    return (
      <svg {...common}>
        <path d="M3 12a9 9 0 1 0 3-6.7" />
        <path d="M3 4v5h5" />
        <path d="M12 7v5l3 2" />
      </svg>
    )
  }

  if (name === 'settings') {
    return (
      <svg {...common}>
        <circle cx="12" cy="12" r="3" />
        <path d="M19 12a7.2 7.2 0 0 0-.1-1l2-1.5-2-3.4-2.4 1a8 8 0 0 0-1.7-1L14.5 3h-5l-.4 3.1a8 8 0 0 0-1.7 1L5 6.1l-2 3.4L5.1 11a7.2 7.2 0 0 0 0 2L3 14.5l2 3.4 2.4-1a8 8 0 0 0 1.7 1l.4 3.1h5l.4-3.1a8 8 0 0 0 1.7-1l2.4 1 2-3.4-2.1-1.5a7.2 7.2 0 0 0 .1-1z" />
      </svg>
    )
  }

  if (name === 'script') {
    return (
      <svg {...common}>
        <path d="M7 4h7l3 3v13H7z" />
        <path d="M14 4v4h4" />
        <path d="M9 12h6" />
        <path d="M9 16h5" />
      </svg>
    )
  }

  if (name === 'image') {
    return (
      <svg {...common}>
        <rect x="3" y="5" width="18" height="14" rx="2" />
        <circle cx="8" cy="10" r="1.5" />
        <path d="M21 16l-5-5-4 4-2-2-5 5" />
      </svg>
    )
  }

  return (
    <svg {...common}>
      <path d="M4 7h16" />
      <path d="M4 12h16" />
      <path d="M4 17h16" />
    </svg>
  )
}

export function HomeWorkspaceHub() {
  const router = useRouter()
  const [isWorkspaceOpen, setIsWorkspaceOpen] = useState(false)
  const [scriptHistory, setScriptHistory] = useState<ScriptHistoryItem[]>([])
  const [slideHistory, setSlideHistory] = useState<SlideHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isStarting, setIsStarting] = useState<'script' | 'slide' | null>(null)
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
          throw new Error('Gagal memuat histori project.')
        }

        const scriptData = (await scriptResponse.json()) as { history?: ScriptHistoryItem[] }
        const slideData = (await slideResponse.json()) as { history?: SlideHistoryItem[] }
        if (!active) return

        setScriptHistory(Array.isArray(scriptData.history) ? scriptData.history : [])
        setSlideHistory(Array.isArray(slideData.history) ? slideData.history : [])
      } catch (err) {
        if (!active) return
        setError(err instanceof Error ? err.message : 'Gagal memuat histori project.')
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

  const historyItems = useMemo<DashboardHistoryItem[]>(() => {
    const scripts = scriptHistory.map((item) => ({
      id: `script-${item.id}`,
      kind: 'script' as const,
      title: item.title,
      summary: item.task_preview || item.selected_source || `${item.moment_count} momen`,
      updated_at: item.updated_at,
      href: `/script?workspace_id=${item.id}` as Route,
    }))

    const slides = slideHistory.map((item) => ({
      id: `slide-${item.id}`,
      kind: 'slide' as const,
      title: item.title,
      summary: item.text_preview || `${item.result_count} result - ${item.embed_count} embed`,
      updated_at: item.updated_at,
      href: `/slides?slide_id=${item.id}` as Route,
    }))

    return [...scripts, ...slides].sort((a, b) => b.updated_at.localeCompare(a.updated_at)).slice(0, 4)
  }, [scriptHistory, slideHistory])

  const startWorkspace = async (kind: 'script' | 'slide') => {
    try {
      setIsStarting(kind)
      setError(null)
      const endpoint = kind === 'script' ? '/script/workspaces' : '/slides/workspace/reset'
      const response = await fetch(buildApiUrl(endpoint), { method: 'POST' })
      if (!response.ok) {
        throw new Error(kind === 'script' ? 'Gagal membuat workspace script.' : 'Gagal membuat postingan gambar.')
      }
      const data = (await response.json()) as { workspace?: { id?: string }; slide?: { id?: string } }
      const nextId = kind === 'script' ? data.workspace?.id : data.slide?.id
      if (!nextId) {
        throw new Error(kind === 'script' ? 'Workspace script baru tidak valid.' : 'Postingan gambar baru tidak valid.')
      }
      router.push(
        kind === 'script'
          ? (`/script?workspace_id=${nextId}` as Route)
          : (`/slides?slide_id=${nextId}` as Route)
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Gagal membuka workspace.')
      setIsStarting(null)
    }
  }

  return (
    <main className="dashboard-shell">
      <aside className="dashboard-sidebar">
        <div className="dashboard-brand">
          <img src="/branding/logo-orviko.png" alt="Logo ORVIKO" className="dashboard-brand__mark" />
          <div className="dashboard-brand__copy">
            <span className="dashboard-brand__name display-font">ORVIKO</span>
            <span className="dashboard-brand__label">Creative OS</span>
          </div>
        </div>

        <nav className="dashboard-nav" aria-label="Navigasi utama">
          <Link href={'/home' as Route} className="dashboard-nav__item is-active">
            <Icon name="dashboard" />
            <span>Dashboard</span>
          </Link>

          <button
            type="button"
            className={`dashboard-nav__item ${isWorkspaceOpen ? 'is-open' : ''}`}
            onClick={() => setIsWorkspaceOpen((value) => !value)}
            aria-expanded={isWorkspaceOpen}
          >
            <Icon name="workspace" />
            <span>Workspace</span>
          </button>

          {isWorkspaceOpen ? (
            <div className="dashboard-subnav">
              <button type="button" className="dashboard-subnav__item" onClick={() => void startWorkspace('script')}>
                <Icon name="script" />
                <span>Script</span>
              </button>
              <button type="button" className="dashboard-subnav__item" onClick={() => void startWorkspace('slide')}>
                <Icon name="image" />
                <span>Postingan Gambar</span>
              </button>
            </div>
          ) : null}

          <Link href={'/history' as Route} className="dashboard-nav__item">
            <Icon name="history" />
            <span>Histori</span>
          </Link>
        </nav>

        <div className="dashboard-sidebar__bottom">
          <button type="button" className="dashboard-nav__item dashboard-nav__item--muted">
            <Icon name="settings" />
            <span>Settings</span>
          </button>
        </div>
      </aside>

      <section className="dashboard-main">
        <header className="dashboard-topbar">
          <div className="dashboard-topbar__title">
            <button type="button" className="dashboard-icon-button" aria-label="Buka menu">
              <Icon name="menu" />
            </button>
            <span>Dashboard</span>
          </div>
          <div className="dashboard-user">
            <span className="dashboard-user__avatar">DS</span>
            <span className="dashboard-user__name">Dony Saputra</span>
          </div>
        </header>

        <section className="dashboard-content">
          <section className="dashboard-section">
            <div className="dashboard-section__intro">
              <p className="section-eyebrow">Menu Cepat</p>
              <h1 className="dashboard-title display-font">Mulai pekerjaan baru</h1>
            </div>
            {error ? <p className="dashboard-error">{error}</p> : null}
            <div className="quick-menu-grid">
              <button
                type="button"
                className="quick-menu-card"
                onClick={() => void startWorkspace('script')}
                disabled={isStarting !== null}
              >
                <span className="quick-menu-card__icon">
                  <Icon name="script" />
                </span>
                <span className="quick-menu-card__content">
                  <span className="quick-menu-card__title">{isStarting === 'script' ? 'Membuka...' : 'Buat Script'}</span>
                  <span className="quick-menu-card__meta">Workspace source sampai momen</span>
                </span>
                <span className="quick-menu-card__arrow">→</span>
              </button>

              <button
                type="button"
                className="quick-menu-card"
                onClick={() => void startWorkspace('slide')}
                disabled={isStarting !== null}
              >
                <span className="quick-menu-card__icon">
                  <Icon name="image" />
                </span>
                <span className="quick-menu-card__content">
                  <span className="quick-menu-card__title">
                    {isStarting === 'slide' ? 'Membuka...' : 'Buat Postingan Gambar'}
                  </span>
                  <span className="quick-menu-card__meta">Workspace visual slide</span>
                </span>
                <span className="quick-menu-card__arrow">→</span>
              </button>
            </div>
          </section>

          <section className="dashboard-section dashboard-section--history">
            <div className="dashboard-section__header">
              <h2 className="dashboard-title display-font">Histori Project</h2>
              <Link href={'/history' as Route} className="dashboard-link">
                Lihat semua
              </Link>
            </div>

            {isLoading ? (
              <p className="dashboard-empty">Memuat histori...</p>
            ) : historyItems.length ? (
              <div className="dashboard-history-grid">
                {historyItems.map((item) => (
                  <Link key={item.id} href={item.href} className="dashboard-history-card">
                    <span className="dashboard-history-card__type">{item.kind === 'script' ? 'Script' : 'Gambar'}</span>
                    <h3>{item.title}</h3>
                    <p>{item.summary}</p>
                    <time>{formatDate(item.updated_at)}</time>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="dashboard-empty">Belum ada histori project.</p>
            )}
          </section>
        </section>
      </section>
    </main>
  )
}
