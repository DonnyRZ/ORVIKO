'use client'

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
  name: string
  title: string
  subtitle: string
  text: string
  design: string
  quantity: number
  position: number
  selected_result_id?: string | null
  embeds: EmbedAsset[]
  results: SlideResult[]
}

const emptySlide: Slide = {
  id: '',
  name: '',
  title: '',
  subtitle: '',
  text: '',
  design: '',
  quantity: 1,
  position: 0,
  selected_result_id: null,
  embeds: [],
  results: [],
}

const normalizeSlide = (slide: Partial<Slide>): Slide => ({
  id: slide.id ?? '',
  name: slide.name ?? 'Slide',
  title: slide.title ?? 'Untitled slide',
  subtitle: slide.subtitle ?? '',
  text: slide.text ?? '',
  design: slide.design ?? '',
  quantity: typeof slide.quantity === 'number' ? slide.quantity : Number(slide.quantity) || 1,
  position: slide.position ?? 0,
  selected_result_id: slide.selected_result_id ?? null,
  embeds: slide.embeds ?? [],
  results: slide.results ?? [],
})

const parseBullets = (text: string) =>
  text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.startsWith('-') || line.startsWith('*'))
    .map((line) => line.replace(/^[-*]\s*/, ''))

const parseBodyLine = (text: string) => {
  const line = text
    .split('\n')
    .map((value) => value.trim())
    .find((value) => value && !value.startsWith('-') && !value.startsWith('*'))
  return line || 'Slide text will appear here.'
}

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
  const [activeSlide, setActiveSlide] = useState(0)
  const [previewSlide, setPreviewSlide] = useState(0)
  const [slides, setSlides] = useState<Slide[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [generatingSlideId, setGeneratingSlideId] = useState<string | null>(null)
  const [generationError, setGenerationError] = useState<string | null>(null)
  const [editingEmbedId, setEditingEmbedId] = useState<string | null>(null)
  const activeSlideData = slides[activeSlide] ?? emptySlide
  const previewSlideData = slides[previewSlide] ?? emptySlide
  const previewResults = previewSlideData.results ?? []
  const selectedResult =
    previewResults.find((card) => card.id === previewSlideData.selected_result_id) ?? previewResults[0] ?? null
  const previewImageUrl =
    selectedResult?.image_path ? `${API_BASE_URL}/results/${selectedResult.id}/image` : null

  const resolveSlideResult = (slide: Slide) =>
    slide.results?.find((card) => card.id === slide.selected_result_id) ?? slide.results?.[0] ?? null

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
      throw new Error('Failed to download image.')
    }
    const blob = await response.blob()
    downloadBlob(blob, filename)
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

      const ratio = 9 / 16
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
  }, [])

  useEffect(() => {
    const handlePointerMove = (event: PointerEvent) => {
      if (!isResizingRef.current || !gridRef.current) return
      const gridRect = gridRef.current.getBoundingClientRect()
      const gridWidth = gridRect.width
      const leftMin = 260
      const centerMin = 320
      const rightMin = 260
      const maxLeft = Math.max(leftMin, gridWidth - centerMin - rightMin)
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

    const loadSlides = async () => {
      try {
        setIsLoading(true)
        const response = await fetch(`${API_BASE_URL}/slides`)
        if (!response.ok) {
          throw new Error(`Failed to load slides (${response.status})`)
        }
        const data = (await response.json()) as { slides?: Slide[] }
        let nextSlides = Array.isArray(data.slides) ? data.slides : []
        if (!nextSlides.length) {
          const createResponse = await fetch(`${API_BASE_URL}/slides`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              name: 'Slide 1',
              title: 'New slide 1',
              subtitle: 'Waiting for content',
              text: '',
              design: '',
              quantity: 1,
              position: 0,
            }),
          })
          if (!createResponse.ok) {
            throw new Error('Failed to create the first slide.')
          }
          const payload = (await createResponse.json()) as { slide: Slide }
          nextSlides = [payload.slide]
        }

        if (!isMounted) return
        const normalized = nextSlides.map((slide) => normalizeSlide(slide))
        setSlides(normalized)
        setActiveSlide((value) => Math.min(value, Math.max(0, normalized.length - 1)))
        setPreviewSlide((value) => Math.min(value, Math.max(0, normalized.length - 1)))
        setLoadError(null)
      } catch (error) {
        if (!isMounted) return
        setLoadError(error instanceof Error ? error.message : 'Failed to load slides.')
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void loadSlides()

    return () => {
      isMounted = false
    }
  }, [])

  const previewStyle =
    previewSize.width && previewSize.height
      ? { width: previewSize.width, height: previewSize.height }
      : undefined

  const previewData = {
    kicker: previewSlideData.name || 'Slide',
    title: previewSlideData.title || 'Slide preview',
    body: parseBodyLine(previewSlideData.text || ''),
    bullets: parseBullets(previewSlideData.text || ''),
    logos: previewSlideData.embeds.map((embed) => embed.label),
  }

  const updateSlideState = (slideId: string, changes: Partial<Slide>) => {
    setSlides((prev) =>
      prev.map((slide) => (slide.id === slideId ? { ...slide, ...changes } : slide)),
    )
  }

  const updateEmbedState = (slideId: string, embedId: string, changes: Partial<EmbedAsset>) => {
    setSlides((prev) =>
      prev.map((slide) => {
        if (slide.id !== slideId) return slide
        return {
          ...slide,
          embeds: slide.embeds.map((embed) => (embed.id === embedId ? { ...embed, ...changes } : embed)),
        }
      }),
    )
  }

  const persistSlide = async (slideId: string, payload: Partial<Slide>) => {
    try {
      const response = await fetch(`${API_BASE_URL}/slides/${slideId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        throw new Error('Failed to save slide changes.')
      }
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Failed to save slide.')
    }
  }

  const refreshSlide = async (slideId: string) => {
    const response = await fetch(`${API_BASE_URL}/slides/${slideId}`)
    if (!response.ok) {
      throw new Error('Failed to refresh slide.')
    }
    const payload = (await response.json()) as { slide: Slide }
    const normalized = normalizeSlide(payload.slide)
    setSlides((prev) => prev.map((slide) => (slide.id === slideId ? normalized : slide)))
  }

  const handleAddSlide = async () => {
    const nextIndex = slides.length + 1
    try {
      const response = await fetch(`${API_BASE_URL}/slides`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: `Slide ${nextIndex}`,
          title: `New slide ${nextIndex}`,
          subtitle: 'Waiting for content',
          text: '',
          design: '',
          quantity: 1,
          position: slides.length,
        }),
      })
      if (!response.ok) {
        throw new Error('Failed to create slide.')
      }
      const payload = (await response.json()) as { slide: Slide }
      const created = normalizeSlide(payload.slide)
      setSlides((prev) => [...prev, created])
      setActiveSlide(nextIndex - 1)
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Failed to create slide.')
    }
  }

  const handleDeleteSlide = async (slideId: string, index: number) => {
    const confirmed = window.confirm('Delete this slide? This cannot be undone.')
    if (!confirmed) return

    try {
      const response = await fetch(`${API_BASE_URL}/slides/${slideId}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        throw new Error('Failed to delete slide.')
      }

      const nextSlides = slides.filter((slide) => slide.id !== slideId)
      if (!nextSlides.length) {
        const createResponse = await fetch(`${API_BASE_URL}/slides`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: 'Slide 1',
            title: 'New slide 1',
            subtitle: 'Waiting for content',
            text: '',
            design: '',
            quantity: 1,
            position: 0,
          }),
        })
        if (!createResponse.ok) {
          throw new Error('Failed to create a new slide.')
        }
        const payload = (await createResponse.json()) as { slide: Slide }
        const created = normalizeSlide(payload.slide)
        setSlides([created])
        setActiveSlide(0)
        setPreviewSlide(0)
        return
      }

      const nextActive = index < activeSlide ? activeSlide - 1 : index === activeSlide ? activeSlide - 1 : activeSlide
      const nextPreview =
        index < previewSlide ? previewSlide - 1 : index === previewSlide ? previewSlide - 1 : previewSlide
      setSlides(nextSlides)
      setActiveSlide(Math.max(0, Math.min(nextActive, nextSlides.length - 1)))
      setPreviewSlide(Math.max(0, Math.min(nextPreview, nextSlides.length - 1)))
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Failed to delete slide.')
    }
  }

  const handleEmbedUpload = async (slideId: string, files: FileList | File[]) => {
    const fileArray = Array.from(files)
    if (!fileArray.length) return

    const invalid = fileArray.find((file) => !file.type.startsWith('image/'))
    if (invalid) {
      setLoadError('Only image files are supported.')
      return
    }

    setLoadError(null)

    try {
      for (const file of fileArray) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('label', file.name)
        formData.append('name', file.name)
        const response = await fetch(`${API_BASE_URL}/slides/${slideId}/embeds`, {
          method: 'POST',
          body: formData,
        })
        if (!response.ok) {
          throw new Error('Failed to upload embed image.')
        }
      }
      await refreshSlide(slideId)
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Failed to upload embed image.')
    }
  }

  const handleEmbedDelete = async (slideId: string, embedId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/embeds/${embedId}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        throw new Error('Failed to delete embed image.')
      }
      await refreshSlide(slideId)
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Failed to delete embed image.')
    }
  }

  const handleEmbedUpdate = async (
    slideId: string,
    embedId: string,
    payload: { label?: string; context?: string },
  ) => {
    try {
      const response = await fetch(`${API_BASE_URL}/embeds/${embedId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        throw new Error('Failed to update embed image.')
      }
      const data = (await response.json()) as { embed: EmbedAsset }
      updateEmbedState(slideId, embedId, data.embed)
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Failed to update embed image.')
    }
  }

  const handleGenerate = async (slideId: string, quantity: number) => {
    setGeneratingSlideId(slideId)
    setGenerationError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/slides/${slideId}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity }),
      })
      if (!response.ok || !response.body) {
        const text = await response.text()
        throw new Error(text || 'Failed to generate images.')
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
            throw new Error(payload.message || 'Generation failed.')
          }
        }
      }

      await refreshSlide(slideId)
    } catch (error) {
      setGenerationError(error instanceof Error ? error.message : 'Failed to generate images.')
    } finally {
      setGeneratingSlideId(null)
    }
  }

  const handleSelectResult = async (slideId: string, resultId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/slides/${slideId}/results/${resultId}/select`, {
        method: 'POST',
      })
      if (!response.ok) {
        throw new Error('Failed to select result.')
      }
      updateSlideState(slideId, { selected_result_id: resultId })
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Failed to select result.')
    }
  }

  const handleDownloadResult = async (slideName: string, result: SlideResult | null) => {
    if (!result || !result.image_path) {
      setLoadError('No image available to download.')
      return
    }
    try {
      const name = slideName || 'slide'
      const title = result.title || 'result'
      await downloadResultImage(result.id, `${name}-${title}.png`)
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Failed to download image.')
    }
  }

  const handleDownloadSelected = async () => {
    await handleDownloadResult(previewSlideData.name, selectedResult)
  }

  const handleDownloadSlidePack = async () => {
    const resultsWithImages = previewResults.filter((result) => result.image_path)
    if (!resultsWithImages.length) {
      setLoadError('No results available to download.')
      return
    }
    try {
      for (const result of resultsWithImages) {
        await handleDownloadResult(previewSlideData.name, result)
      }
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Failed to download slide pack.')
    }
  }

  const handleDownloadAllSlides = async () => {
    const targets = slides
      .map((slide) => ({ slide, result: resolveSlideResult(slide) }))
      .filter(
        (item): item is { slide: Slide; result: SlideResult } =>
          Boolean(item.result && item.result.image_path),
      )
    if (!targets.length) {
      setLoadError('No generated slides to download.')
      return
    }
    try {
      for (const target of targets) {
        await handleDownloadResult(target.slide.name, target.result)
      }
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Failed to download all slides.')
    }
  }

  const handleDeleteResult = async (slideId: string, resultId: string) => {
    const confirmed = window.confirm('Delete this generated result?')
    if (!confirmed) return
    try {
      const response = await fetch(`${API_BASE_URL}/results/${resultId}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        throw new Error('Failed to delete result.')
      }
      await refreshSlide(slideId)
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Failed to delete result.')
    }
  }

  return (
    <main className="workspace-shell">
      <header className="workspace-header">
        <div className="brand">
          <div className="brand-mark">OD</div>
          <div className="brand-copy">
            <p className="brand-title display-font">ODIN TikTok Slide</p>
            <p className="brand-subtitle">Workspace for 9:16 slide images</p>
          </div>
          <span className="tag tag-accent">1080 x 1920</span>
        </div>
        <div className="header-actions">
          <button className="btn btn-ghost" type="button" onClick={handleDownloadAllSlides}>
            Download all slides
          </button>
          <button className="btn btn-primary" type="button" onClick={handleDownloadSelected}>
            Download selected
          </button>
        </div>
      </header>

      <div className="workspace-grid" ref={gridRef} style={{ ['--left-width' as const]: `${leftWidth}px` }}>
        <aside className="workspace-column workspace-column--left workspace-column--scroll">
          <button
            className="column-resizer"
            type="button"
            aria-label="Resize left panel"
            onPointerDown={(event) => {
              event.preventDefault()
              isResizingRef.current = true
              document.body.classList.add('is-resizing')
            }}
          />
          {loadError ? <p className="field__hint">{loadError}</p> : null}
          {isLoading ? <p className="field__hint">Loading slides...</p> : null}
          {slides.map((slide, index) => {
            const isActive = activeSlide === index
            const isGenerating = generatingSlideId === slide.id

            return (
              <section className="column-section" key={slide.id}>
                <header className="section-header">
                  <div>
                    <p className="section-eyebrow">{slide.name}</p>
                    <h2 className="section-title display-font">{slide.title}</h2>
                    <p className="section-subtitle">{slide.subtitle}</p>
                  </div>
                  <div className="section-actions section-actions--row">
                    <button
                      className="btn btn-outline btn-small"
                      type="button"
                      onClick={() => setActiveSlide(index)}
                    >
                      {isActive ? 'Active' : 'Open'}
                    </button>
                    <button
                      className="btn btn-ghost btn-small btn-danger"
                      type="button"
                      onClick={() => handleDeleteSlide(slide.id, index)}
                    >
                      Delete
                    </button>
                  </div>
                </header>

                {isActive ? (
                  <>
                    <div className="field">
                      <p className="field__label">Embed images</p>
                      <div className="upload-row">
                        <input
                          id={`embed-input-${slide.id}`}
                          className="sr-only"
                          type="file"
                          accept="image/*"
                          multiple
                          onChange={(event) => {
                            const files = event.target.files
                            if (files?.length) {
                              void handleEmbedUpload(slide.id, files)
                            }
                            event.target.value = ''
                          }}
                        />
                        <label className="upload-slot" htmlFor={`embed-input-${slide.id}`} aria-label="Upload embed image">
                          +
                        </label>
                        {slide.embeds.map((asset) => {
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
                                  onClick={() => handleEmbedDelete(slide.id, asset.id)}
                                  aria-label={`Remove ${asset.name}`}
                                >
                                  x
                                </button>
                                <button
                                  className="embed-thumb__edit"
                                  type="button"
                                  onClick={() => setEditingEmbedId(isEditing ? null : asset.id)}
                                >
                                  Edit
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
                                    onChange={(event) =>
                                      updateEmbedState(slide.id, asset.id, { label: event.target.value })
                                    }
                                    onBlur={(event) =>
                                      handleEmbedUpdate(slide.id, asset.id, {
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
                                    onChange={(event) =>
                                      updateEmbedState(slide.id, asset.id, { context: event.target.value })
                                    }
                                    onBlur={(event) =>
                                      handleEmbedUpdate(slide.id, asset.id, {
                                        label: asset.label,
                                        context: event.target.value,
                                      })
                                    }
                                    placeholder="Official logo, use for Gemini mentions."
                                  />
                                </div>
                              ) : null}
                            </div>
                          )
                        })}
                      </div>
                      <p className="field__hint">
                        Upload logos or icons so the generator can use the correct visuals.
                      </p>
                    </div>

                    <div className="field">
                      <label className="field__label" htmlFor={`slide-${index}-text`}>
                        Slide text
                      </label>
                      <textarea
                        id={`slide-${index}-text`}
                        className="field__input field__input--area"
                        rows={6}
                        value={slide.text}
                        onChange={(event) => updateSlideState(slide.id, { text: event.target.value })}
                        onBlur={() => persistSlide(slide.id, { text: slide.text })}
                      />
                      <p className="field__hint">Text will be used 100 percent inside the slide.</p>
                    </div>

                    <div className="field">
                      <label className="field__label" htmlFor={`slide-${index}-notes`}>
                        User notes (optional)
                      </label>
                      <textarea
                        id={`slide-${index}-notes`}
                        className="field__input field__input--area"
                        rows={4}
                        value={slide.design}
                        onChange={(event) => updateSlideState(slide.id, { design: event.target.value })}
                        onBlur={() => persistSlide(slide.id, { design: slide.design })}
                        placeholder="Notes: preferred colors, anime vibe, or extra context (not shown as slide text)."
                      />
                      <p className="field__hint">Notes are guidance only and will not appear as slide text.</p>
                    </div>

                    <div className="field-row">
                      <div className="field">
                        <label className="field__label" htmlFor={`slide-${index}-quantity`}>
                          Image quantity
                        </label>
                        <select
                          id={`slide-${index}-quantity`}
                          className="field__input"
                          value={slide.quantity}
                          onChange={(event) => {
                            const nextValue = Number(event.target.value)
                            updateSlideState(slide.id, { quantity: nextValue })
                            void persistSlide(slide.id, { quantity: nextValue })
                          }}
                        >
                          <option value={1}>1 image</option>
                          <option value={2}>2 images</option>
                          <option value={3}>3 images</option>
                          <option value={4}>4 images</option>
                          <option value={5}>5 images</option>
                        </select>
                      </div>
                      <button
                        className="btn btn-primary btn-wide"
                        type="button"
                        onClick={() => handleGenerate(slide.id, slide.quantity)}
                        disabled={isGenerating}
                      >
                        {isGenerating ? 'Generating...' : 'Generate images'}
                      </button>
                    </div>
                    {generationError && isActive ? (
                      <p className="field__hint">{generationError}</p>
                    ) : null}
                  </>
                ) : null}
              </section>
            )
          })}

          <div className="column-section column-section--tight">
            <button className="add-slide" type="button" onClick={handleAddSlide}>
              + Add new slide
            </button>
          </div>
        </aside>

        <section className="workspace-column workspace-column--center">
          <section className="column-section column-section--fill">
            <header className="section-header section-header--compact">
              <div>
                <p className="section-eyebrow">Slide preview</p>
                <h2 className="section-title display-font">
                  {previewSlideData.name || 'Slide'} - {selectedResult?.title || 'No result'}
                </h2>
                <p className="section-subtitle">Preview reflects the selected result on the right.</p>
              </div>
              <div className="section-actions section-actions--row">
                <div className="preview-nav">
                  <button
                    className="btn btn-ghost btn-small"
                    type="button"
                    aria-label="Previous slide"
                    onClick={() => setPreviewSlide((value) => Math.max(0, value - 1))}
                    disabled={previewSlide === 0}
                  >
                    {'<'}
                  </button>
                  <button
                    className="btn btn-ghost btn-small"
                    type="button"
                    aria-label="Next slide"
                    onClick={() => setPreviewSlide((value) => Math.min(slides.length - 1, value + 1))}
                    disabled={previewSlide === slides.length - 1}
                  >
                    {'>'}
                  </button>
                </div>
                <button className="btn btn-outline btn-small" type="button" onClick={handleDownloadSelected}>
                  Download image
                </button>
              </div>
            </header>
            <div className="preview-stage" ref={previewStageRef}>
              <div className="preview-frame" style={previewStyle}>
                {previewImageUrl ? (
                  <div className="preview-image-wrapper">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={previewImageUrl} alt="Slide preview" className="preview-image" />
                  </div>
                ) : (
                  <div className="preview-canvas">
                    <div className="preview-top">
                      <span className="preview-kicker">{previewData.kicker}</span>
                      <span className="preview-pill">{previewSlideData.name || 'Slide'}</span>
                    </div>
                    <h3 className="preview-title display-font">{previewData.title}</h3>
                    <p className="preview-body">{previewData.body}</p>
                    {previewData.bullets.length ? (
                      <ul className="preview-list">
                        {previewData.bullets.map((bullet) => (
                          <li key={bullet}>{bullet}</li>
                        ))}
                      </ul>
                    ) : null}
                    <div className="preview-logos">
                      {previewData.logos.map((logo) => (
                        <span key={logo} className="logo-chip">
                          {logo}
                        </span>
                      ))}
                    </div>
                    <div className="preview-footer">
                      <span>1080 x 1920 px</span>
                      <span>
                        {selectedResult ? `${selectedResult.title} - ${selectedResult.note}` : 'No result yet'}
                      </span>
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
                <p className="section-eyebrow">Generated results</p>
                <h2 className="section-title display-font">{previewSlideData.name || 'Slide'} outputs</h2>
                <p className="section-subtitle">Pick a result to preview or download.</p>
              </div>
              <div className="section-actions">
                <button className="btn btn-ghost btn-small" type="button" onClick={handleDownloadSlidePack}>
                  Download slide pack
                </button>
                <button className="btn btn-primary btn-small" type="button" onClick={handleDownloadSelected}>
                  Download selected
                </button>
              </div>
            </header>
          </section>
          <section className="column-section">
            <div className="slide-tabs">
              {slides.map((slide, index) => (
                <button
                  key={slide.id}
                  className={`tab${previewSlide === index ? ' is-active' : ''}`}
                  type="button"
                  aria-disabled="true"
                >
                  {slide.name}
                </button>
              ))}
            </div>

            <div className="result-grid">
              {previewResults.length ? (
                previewResults.map((card) => {
                  const isSelected = card.id === previewSlideData.selected_result_id
                  const imageUrl = card.image_path
                    ? `${API_BASE_URL}/results/${card.id}/image`
                    : null

                  return (
                    <article key={card.id} className="result-card" data-selected={isSelected ? 'true' : 'false'}>
                      <div className="result-thumb" data-tone={card.tone}>
                        {imageUrl ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img src={imageUrl} alt={card.title} className="result-thumb__image" />
                        ) : (
                          '9:16'
                        )}
                      </div>
                      {isSelected ? <span className="selected-badge">Selected</span> : null}
                      <div className="result-meta">
                        <div>
                          <p className="result-title">{card.title}</p>
                          <p className="result-caption">{card.note}</p>
                        </div>
                        <div className="result-actions">
                          <button
                            className="btn btn-outline btn-small"
                            type="button"
                            onClick={() => handleDownloadResult(previewSlideData.name, card)}
                          >
                            Download
                          </button>
                          <button
                            className="btn btn-ghost btn-small btn-danger"
                            type="button"
                            onClick={() => handleDeleteResult(previewSlideData.id, card.id)}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                      <button
                        className="btn btn-ghost btn-small"
                        type="button"
                        onClick={() => handleSelectResult(previewSlideData.id, card.id)}
                      >
                        Use for preview
                      </button>
                    </article>
                  )
                })
              ) : (
                <p className="field__hint">No generated results yet.</p>
              )}
            </div>
          </section>
        </aside>
      </div>
    </main>
  )
}
