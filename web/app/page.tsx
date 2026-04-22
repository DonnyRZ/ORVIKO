'use client'

import type { CSSProperties } from 'react'
import { useEffect, useRef, useState } from 'react'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://127.0.0.1:8000'

type EmbedAsset = {
  id: string
  slide_id: string
  label: string
  name: string
  context?: string | null
  file_path: string
  mime_type: string
  size: number
  created_at: string
}

type SlideResult = {
  id: string
  slide_id: string
  title: string
  note: string
  tone: string
  status: string
  image_path?: string | null
  created_at: string
  updated_at: string
}

type Slide = {
  id: string
  title: string
  text: string
  design: string
  quantity: number
  aspect_ratio: '1:1' | '4:5' | '9:16' | '16:9'
  selected_result_id?: string | null
  embeds: EmbedAsset[]
  results: SlideResult[]
}

const ASPECT_RATIO_OPTIONS = ['1:1', '4:5', '9:16', '16:9'] as const

const emptySlide: Slide = {
  id: '',
  title: 'Slide tanpa judul',
  text: '',
  design: '',
  quantity: 1,
  aspect_ratio: '9:16',
  selected_result_id: null,
  embeds: [],
  results: [],
}

const normalizeAspectRatio = (value: unknown): Slide['aspect_ratio'] =>
  ASPECT_RATIO_OPTIONS.includes(value as Slide['aspect_ratio']) ? (value as Slide['aspect_ratio']) : '9:16'

const normalizeSlide = (slide: Partial<Slide>): Slide => ({
  id: slide.id ?? '',
  title: slide.title ?? 'Slide tanpa judul',
  text: slide.text ?? '',
  design: slide.design ?? '',
  quantity: typeof slide.quantity === 'number' ? slide.quantity : Number(slide.quantity) || 1,
  aspect_ratio: normalizeAspectRatio(slide.aspect_ratio),
  selected_result_id: slide.selected_result_id ?? null,
  embeds: slide.embeds ?? [],
  results: slide.results ?? [],
})

const parseSseEvent = (chunk: string) => {
  const lines = chunk.split('\n')
  let eventName = 'message'
  const dataLines: string[] = []

  lines.forEach((line) => {
    if (line.startsWith('event:')) {
      eventName = line.replace('event:', '').trim()
    } else if (line.startsWith('data:')) {
      dataLines.push(line.replace('data:', '').trim())
    }
  })

  return { event: eventName, data: dataLines.join('\n') }
}

export default function Page() {
  const gridRef = useRef<HTMLDivElement | null>(null)
  const previewStageRef = useRef<HTMLDivElement | null>(null)
  const [previewSize, setPreviewSize] = useState({ width: 0, height: 0 })
  const [leftWidth, setLeftWidth] = useState(320)
  const isResizingRef = useRef(false)
  const [currentSlide, setCurrentSlide] = useState<Slide>(emptySlide)
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationError, setGenerationError] = useState<string | null>(null)
  const [editingEmbedId, setEditingEmbedId] = useState<string | null>(null)

  const currentResults = currentSlide.results ?? []
  const selectedResult =
    currentResults.find((card) => card.id === currentSlide.selected_result_id) ?? currentResults[0] ?? null
  const previewImageUrl =
    selectedResult?.image_path ? `${API_BASE_URL}/results/${selectedResult.id}/image` : null
  const slideTitle = currentSlide.title.trim() || 'Slide tanpa judul'
  const slideFileLabel = currentSlide.title.trim() || 'slide'
  const activeAspectRatio = currentSlide.aspect_ratio || '9:16'
  const [aspectWidth, aspectHeight] = activeAspectRatio.split(':').map(Number)
  const aspectRatioValue = `${aspectWidth} / ${aspectHeight}`
  const isLandscapeRatio = aspectWidth > aspectHeight
  const resultThumbStyle = { ['--result-aspect-ratio' as '--result-aspect-ratio']: aspectRatioValue } as CSSProperties

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  }

  const downloadResultImage = async (resultId: string, filename: string) => {
    const response = await fetch(`${API_BASE_URL}/results/${resultId}/image`)
    if (!response.ok) {
      throw new Error('Gagal download gambar.')
    }
    const blob = await response.blob()
    downloadBlob(blob, filename)
  }

  const loadCurrentSlide = async () => {
    const response = await fetch(`${API_BASE_URL}/slides`)
    if (!response.ok) {
      throw new Error(`Gagal memuat slide (${response.status})`)
    }
    const data = (await response.json()) as { slides?: Slide[] }
    const nextSlide = Array.isArray(data.slides) ? data.slides[0] : null
    if (!nextSlide) {
      throw new Error('Tidak ada slide tersedia.')
    }
    const normalized = normalizeSlide(nextSlide)
    setCurrentSlide(normalized)
    setGenerationError(null)
    setLoadError(null)
    return normalized
  }

  useEffect(() => {
    const stage = previewStageRef.current
    if (!stage) return

    const updateSize = () => {
      const styles = window.getComputedStyle(stage)
      const paddingX = parseFloat(styles.paddingLeft) + parseFloat(styles.paddingRight)
      const paddingY = parseFloat(styles.paddingTop) + parseFloat(styles.paddingBottom)
      const maxWidth = stage.clientWidth - paddingX
      const maxHeight = stage.clientHeight - paddingY

      if (maxWidth <= 0 || maxHeight <= 0) return

      const [widthUnits, heightUnits] = activeAspectRatio.split(':').map(Number)
      const ratio = widthUnits / heightUnits
      let width = maxWidth
      let height = width / ratio

      if (height > maxHeight) {
        height = maxHeight
        width = height * ratio
      }

      setPreviewSize({ width: Math.floor(width), height: Math.floor(height) })
    }

    updateSize()

    if (typeof ResizeObserver === 'undefined') {
      window.addEventListener('resize', updateSize)
      return () => window.removeEventListener('resize', updateSize)
    }

    const observer = new ResizeObserver(() => {
      window.requestAnimationFrame(updateSize)
    })
    observer.observe(stage)

    return () => observer.disconnect()
  }, [activeAspectRatio])

  useEffect(() => {
    const handlePointerMove = (event: PointerEvent) => {
      if (!isResizingRef.current || !gridRef.current) return
      const gridRect = gridRef.current.getBoundingClientRect()
      const gridWidth = gridRect.width
      const dividerWidth = 12
      const leftMin = 260
      const centerMin = 480
      const rightMin = 260
      const maxLeft = Math.max(leftMin, gridWidth - dividerWidth - centerMin - rightMin)
      const nextWidth = Math.min(Math.max(event.clientX - gridRect.left, leftMin), maxLeft)
      setLeftWidth(nextWidth)
    }

    const handlePointerUp = () => {
      if (!isResizingRef.current) return
      isResizingRef.current = false
      document.body.classList.remove('is-resizing')
    }

    window.addEventListener('pointermove', handlePointerMove)
    window.addEventListener('pointerup', handlePointerUp)

    return () => {
      window.removeEventListener('pointermove', handlePointerMove)
      window.removeEventListener('pointerup', handlePointerUp)
    }
  }, [])

  useEffect(() => {
    let isMounted = true

    const bootstrap = async () => {
      try {
        setIsLoading(true)
        await loadCurrentSlide()
      } catch (error) {
        if (!isMounted) return
        setLoadError(error instanceof Error ? error.message : 'Gagal memuat slide.')
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void bootstrap()

    return () => {
      isMounted = false
    }
  }, [])

  const previewStyle =
    previewSize.width && previewSize.height
      ? { width: previewSize.width, height: previewSize.height }
      : undefined

  const updateSlideState = (changes: Partial<Slide>) => {
    setCurrentSlide((prev) => ({ ...prev, ...changes }))
  }

  const updateEmbedState = (embedId: string, changes: Partial<EmbedAsset>) => {
    setCurrentSlide((prev) => ({
      ...prev,
      embeds: prev.embeds.map((embed) => (embed.id === embedId ? { ...embed, ...changes } : embed)),
    }))
  }

  const persistSlide = async (payload: Partial<Slide>) => {
    try {
      const response = await fetch(`${API_BASE_URL}/slides/${currentSlide.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        throw new Error('Gagal menyimpan perubahan slide.')
      }
      const data = (await response.json()) as { slide: Slide }
      setCurrentSlide((prev) => ({ ...prev, ...normalizeSlide(data.slide), embeds: prev.embeds, results: prev.results }))
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Gagal menyimpan slide.')
    }
  }

  const refreshSlide = async () => {
    const response = await fetch(`${API_BASE_URL}/slides/${currentSlide.id}`)
    if (!response.ok) {
      throw new Error('Gagal memperbarui slide.')
    }
    const payload = (await response.json()) as { slide: Slide }
    setCurrentSlide(normalizeSlide(payload.slide))
  }

  const handleDeleteSlide = async () => {
    const confirmed = window.confirm('Reset slide ini? Slide kosong baru akan dibuat langsung.')
    if (!confirmed) return

    try {
      const response = await fetch(`${API_BASE_URL}/slides/${currentSlide.id}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        throw new Error('Gagal Reset slide.')
      }
      const payload = (await response.json()) as { slide?: Slide }
      if (payload.slide) {
        setCurrentSlide(normalizeSlide(payload.slide))
      } else {
        await loadCurrentSlide()
      }
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Gagal Reset slide.')
    }
  }

  const handleEmbedUpload = async (files: FileList | File[]) => {
    const fileArray = Array.from(files)
    if (!fileArray.length) return

    const invalid = fileArray.find((file) => !file.type.startsWith('image/'))
    if (invalid) {
      setLoadError('Hanya file gambar yang didukung.')
      return
    }

    setLoadError(null)

    try {
      for (const file of fileArray) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('label', file.name)
        formData.append('name', file.name)
        const response = await fetch(`${API_BASE_URL}/slides/${currentSlide.id}/embeds`, {
          method: 'POST',
          body: formData,
        })
        if (!response.ok) {
          throw new Error('Gagal upload gambar embed.')
        }
      }
      await refreshSlide()
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Gagal upload gambar embed.')
    }
  }

  const handleEmbedDelete = async (embedId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/embeds/${embedId}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        throw new Error('Gagal menghapus gambar embed.')
      }
      await refreshSlide()
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Gagal menghapus gambar embed.')
    }
  }

  const handleEmbedUpdate = async (embedId: string, payload: { label?: string; context?: string }) => {
    try {
      const response = await fetch(`${API_BASE_URL}/embeds/${embedId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        throw new Error('Gagal memperbarui gambar embed.')
      }
      const data = (await response.json()) as { embed: EmbedAsset }
      updateEmbedState(embedId, data.embed)
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Gagal memperbarui gambar embed.')
    }
  }

  const handleGenerate = async () => {
    setIsGenerating(true)
    setGenerationError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/slides/${currentSlide.id}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: currentSlide.quantity }),
      })
      if (!response.ok || !response.body) {
        const text = await response.text()
        throw new Error(text || 'Gagal generate gambar.')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        let boundary = buffer.indexOf('\n\n')
        while (boundary !== -1) {
          const rawEvent = buffer.slice(0, boundary).trim()
          buffer = buffer.slice(boundary + 2)
          boundary = buffer.indexOf('\n\n')
          if (!rawEvent) continue
          const parsed = parseSseEvent(rawEvent)
          if (parsed.event === 'error') {
            const payload = JSON.parse(parsed.data) as { message?: string }
            throw new Error(payload.message || 'Generate gagal.')
          }
        }
      }

      await refreshSlide()
    } catch (error) {
      setGenerationError(error instanceof Error ? error.message : 'Gagal generate gambar.')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSelectResult = async (resultId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/slides/${currentSlide.id}/results/${resultId}/select`, {
        method: 'POST',
      })
      if (!response.ok) {
        throw new Error('Gagal memilih result.')
      }
      updateSlideState({ selected_result_id: resultId })
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Gagal memilih result.')
    }
  }

  const handleDownloadResult = async (result: SlideResult | null) => {
    if (!result || !result.image_path) {
      setLoadError('Tidak ada gambar untuk di-download.')
      return
    }
    try {
      const title = result.title || 'result'
      await downloadResultImage(result.id, `${slideFileLabel}-${title}.png`)
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Gagal download gambar.')
    }
  }

  const handleDownloadSelected = async () => {
    await handleDownloadResult(selectedResult)
  }

  const handleDownloadAllResults = async () => {
    const resultsWithImages = currentResults.filter((result) => result.image_path)
    if (!resultsWithImages.length) {
      setLoadError('Tidak ada result untuk di-download.')
      return
    }
    try {
      for (const result of resultsWithImages) {
        await handleDownloadResult(result)
      }
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Gagal download result slide.')
    }
  }

  const handleDeleteResult = async (resultId: string) => {
    const confirmed = window.confirm('Hapus result yang dihasilkan ini?')
    if (!confirmed) return
    try {
      const response = await fetch(`${API_BASE_URL}/results/${resultId}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        throw new Error('Gagal menghapus result.')
      }
      await refreshSlide()
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Gagal menghapus result.')
    }
  }

  return (
    <main className="workspace-shell">
      <header className="workspace-header">
        <div className="brand">
          <div className="brand-mark">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/branding/logo-odin.png" alt="Logo ODIN" className="brand-mark__image" />
          </div>
          <div className="brand-copy">
            <p className="brand-title display-font">ODIN Slide</p>
            <p className="brand-subtitle">Workspace untuk satu gambar slide</p>
          </div>
          <span className="tag tag-accent">{activeAspectRatio}</span>
        </div>
        <div className="header-actions">
                <button className="btn btn-ghost" type="button" onClick={handleDownloadAllResults} disabled={!currentResults.length}>
                  Download semua result
                </button>
                <button className="btn btn-primary" type="button" onClick={handleDownloadSelected} disabled={!selectedResult}>
                  Download yang dipilih
                </button>
        </div>
      </header>

      <div
        className="workspace-grid"
        ref={gridRef}
        style={{ ['--left-width' as '--left-width']: `${leftWidth}px` } as CSSProperties}
      >
        <aside className="workspace-column workspace-column--left workspace-column--scroll">
          {loadError ? <p className="field__hint">{loadError}</p> : null}
          {isLoading ? <p className="field__hint">Memuat slide...</p> : null}

          <section className="column-section">
            <header className="section-header">
              <div>
                <p className="section-eyebrow">Slide aktif</p>
                <h2 className="section-title display-font">{slideTitle}</h2>
              </div>
              <div className="section-actions section-actions--row">
                <button className="btn btn-ghost btn-small btn-danger" type="button" onClick={handleDeleteSlide} disabled={!currentSlide.id}>
                  Reset
                </button>
              </div>
            </header>

            <div className="field">
              <label className="field__label" htmlFor="slide-title">
                Judul slide
              </label>
              <input
                id="slide-title"
                className="field__input"
                value={currentSlide.title}
                onChange={(event) => updateSlideState({ title: event.target.value })}
                onBlur={() => persistSlide({ title: currentSlide.title })}
                placeholder="Slide tanpa judul"
              />
            </div>

            <div className="field">
              <p className="field__label">Gambar embed</p>
              <div className="upload-row">
                <input
                  id={`embed-input-${currentSlide.id || 'single'}`}
                  className="sr-only"
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={(event) => {
                    const files = event.target.files
                    if (files?.length) {
                      void handleEmbedUpload(files)
                    }
                    event.target.value = ''
                  }}
                />
                <label className="upload-slot" htmlFor={`embed-input-${currentSlide.id || 'single'}`} aria-label="Upload gambar embed">
                  +
                </label>
                {currentSlide.embeds.map((asset) => {
                  const isEditing = editingEmbedId === asset.id
                  const contextValue = asset.context ?? ''
                  return (
                    <div key={asset.id} className="embed-item" aria-label={asset.name}>
                      <div className="embed-thumb">
                        <img
                          src={`${API_BASE_URL}/embeds/${asset.id}/file`}
                          alt={asset.name}
                          className="embed-thumb__image"
                        />
                        <button
                          className="embed-thumb__remove"
                          type="button"
                          onClick={() => handleEmbedDelete(asset.id)}
                          aria-label={`Hapus ${asset.name}`}
                        >
                          x
                        </button>
                        <button
                          className="embed-thumb__edit"
                          type="button"
                          onClick={() => setEditingEmbedId(isEditing ? null : asset.id)}
                        >
                          Ubah
                        </button>
                      </div>
                      {isEditing ? (
                        <div className="embed-edit">
                          <label className="field__label" htmlFor={`embed-label-${asset.id}`}>
                            Label/Brand
                          </label>
                          <input
                            id={`embed-label-${asset.id}`}
                            className="field__input field__input--compact"
                            value={asset.label}
                            onChange={(event) => updateEmbedState(asset.id, { label: event.target.value })}
                            onBlur={(event) =>
                              handleEmbedUpdate(asset.id, {
                                label: event.target.value,
                                context: contextValue,
                              })
                            }
                            placeholder="Gemini"
                          />
                          <label className="field__label" htmlFor={`embed-context-${asset.id}`}>
                            Context
                          </label>
                          <textarea
                            id={`embed-context-${asset.id}`}
                            className="field__input field__input--area"
                            rows={2}
                            value={contextValue}
                            onChange={(event) => updateEmbedState(asset.id, { context: event.target.value })}
                            onBlur={(event) =>
                              handleEmbedUpdate(asset.id, {
                                label: asset.label,
                                context: event.target.value,
                              })
                            }
                            placeholder="Logo resmi, pakai untuk mention Gemini."
                          />
                        </div>
                      ) : null}
                    </div>
                  )
                })}
              </div>
              <p className="field__hint">Upload logo atau ikon agar generator memakai visual yang tepat.</p>
            </div>

            <div className="field">
              <label className="field__label" htmlFor="slide-text">
                Teks slide
              </label>
              <textarea
                id="slide-text"
                className="field__input field__input--area"
                rows={6}
                value={currentSlide.text}
                onChange={(event) => updateSlideState({ text: event.target.value })}
                onBlur={() => persistSlide({ text: currentSlide.text })}
              />
              <p className="field__hint">Teks ini akan dipakai 100 persen di dalam slide.</p>
            </div>

            <div className="field">
              <label className="field__label" htmlFor="slide-notes">
                Catatan pengguna (opsional)
              </label>
              <textarea
                id="slide-notes"
                className="field__input field__input--area"
                rows={4}
                value={currentSlide.design}
                onChange={(event) => updateSlideState({ design: event.target.value })}
                onBlur={() => persistSlide({ design: currentSlide.design })}
                placeholder="Catatan: warna pilihan, vibe anime, atau context tambahan (tidak tampil sebagai teks slide)."
              />
              <p className="field__hint">Catatan hanya menjadi arahan dan tidak akan muncul sebagai teks slide.</p>
            </div>

            <div className="field-row">
              <div className="field">
                <label className="field__label" htmlFor="slide-aspect-ratio">
                  Aspect ratio
                </label>
                <select
                  id="slide-aspect-ratio"
                  className="field__input"
                  value={currentSlide.aspect_ratio}
                  onChange={(event) => {
                    const nextValue = normalizeAspectRatio(event.target.value)
                    updateSlideState({ aspect_ratio: nextValue })
                    void persistSlide({ aspect_ratio: nextValue })
                  }}
                >
                  {ASPECT_RATIO_OPTIONS.map((ratio) => (
                    <option key={ratio} value={ratio}>
                      {ratio}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label className="field__label" htmlFor="slide-quantity">
                  Jumlah gambar
                </label>
                <select
                  id="slide-quantity"
                  className="field__input"
                  value={currentSlide.quantity}
                  onChange={(event) => {
                    const nextValue = Number(event.target.value)
                    updateSlideState({ quantity: nextValue })
                    void persistSlide({ quantity: nextValue })
                  }}
                >
                  <option value={1}>1 gambar</option>
                  <option value={2}>2 gambar</option>
                  <option value={3}>3 gambar</option>
                  <option value={4}>4 gambar</option>
                  <option value={5}>5 gambar</option>
                </select>
              </div>
            </div>
            <button className="btn btn-primary btn-wide field-action" type="button" onClick={handleGenerate} disabled={isGenerating || !currentSlide.id}>
              {isGenerating ? 'Sedang generate...' : 'Generate gambar'}
            </button>
            {generationError ? <p className="field__hint">{generationError}</p> : null}
          </section>
        </aside>
        <button
          className="column-resizer"
          type="button"
          aria-label="Ubah lebar panel kiri"
          onPointerDown={(event) => {
            event.preventDefault()
            isResizingRef.current = true
            document.body.classList.add('is-resizing')
          }}
        />

        <section className="workspace-column workspace-column--center">
          <section className="column-section column-section--fill">
            <header className="section-header section-header--compact">
              <div>
                <p className="section-eyebrow">Preview slide</p>
                <h2 className="section-title display-font">
                  {selectedResult ? `${slideTitle} - ${selectedResult.title}` : 'Preview belum tersedia'}
                </h2>
                <p className="section-subtitle">
                  {selectedResult
                    ? 'Preview mengikuti result yang dipilih di kanan.'
                    : 'Preview akan muncul setelah gambar berhasil dibuat.'}
                </p>
              </div>
              <div className="section-actions section-actions--row">
                <button className="btn btn-outline btn-small" type="button" onClick={handleDownloadSelected} disabled={!selectedResult}>
                  Download gambar
                </button>
              </div>
            </header>
            <div className="preview-stage" ref={previewStageRef}>
              <div className="preview-frame" style={previewStyle}>
                {previewImageUrl ? (
                  <div className="preview-image-wrapper">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={previewImageUrl} alt="Preview slide" className="preview-image" />
                  </div>
                ) : (
                  <div className="preview-canvas">
                    <div className="preview-top">
                      <span className="preview-kicker">Preview slide</span>
                      <span className="preview-pill">Menunggu result</span>
                    </div>
                    <h3 className="preview-title display-font">Belum ada gambar</h3>
                    <p className="preview-body">Area ini hanya menampilkan hasil final setelah proses generate selesai.</p>
                    <div className="preview-footer">
                      <span>{activeAspectRatio}</span>
                      <span>Belum ada result</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </section>
        </section>

        <aside className="workspace-column workspace-column--right workspace-column--scroll">
          <section className="column-section">
            <header className="section-header">
              <div>
                <p className="section-eyebrow">Result yang dihasilkan</p>
                <h2 className="section-title display-font">Result {slideTitle}</h2>
                <p className="section-subtitle">Pilih result untuk preview atau download.</p>
              </div>
            </header>
          </section>
          <section className="column-section">
            <div className="result-grid">
              {currentResults.length ? (
                currentResults.map((card) => {
                  const isSelected = card.id === currentSlide.selected_result_id
                  const imageUrl = card.image_path ? `${API_BASE_URL}/results/${card.id}/image` : null

                  return (
                    <article
                      key={card.id}
                      className="result-card"
                      data-selected={isSelected ? 'true' : 'false'}
                      data-landscape={isLandscapeRatio ? 'true' : 'false'}
                    >
                      <div className="result-thumb" data-tone={card.tone} style={resultThumbStyle}>
                        {imageUrl ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img src={imageUrl} alt={card.title} className="result-thumb__image" />
                        ) : (
                          activeAspectRatio
                        )}
                      </div>
                      {isSelected ? <span className="selected-badge">Dipilih</span> : null}
                      <div className="result-meta">
                        <div>
                          <p className="result-title">{card.title}</p>
                          <p className="result-caption">{card.note}</p>
                        </div>
                        <div className="result-actions">
                          <button className="btn btn-outline btn-small" type="button" onClick={() => handleDownloadResult(card)}>
                            Download
                          </button>
                          <button
                            className="btn btn-ghost btn-small btn-danger"
                            type="button"
                            onClick={() => handleDeleteResult(card.id)}
                          >
                            Hapus
                          </button>
                        </div>
                      </div>
                      <button className="btn btn-ghost btn-small" type="button" onClick={() => handleSelectResult(card.id)}>
                        Pakai untuk preview
                      </button>
                    </article>
                  )
                })
              ) : (
                <p className="field__hint">Belum ada result yang dihasilkan.</p>
              )}
            </div>
          </section>
        </aside>
      </div>
    </main>
  )
}
