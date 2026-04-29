const normalizeBaseUrl = (value: string | undefined) => {
  if (!value) return ''
  return value.endsWith('/') ? value.slice(0, -1) : value
}

const API_BASE_URL = normalizeBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL)

export const buildApiUrl = (path: string) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return API_BASE_URL ? `${API_BASE_URL}${normalizedPath}` : normalizedPath
}

export const buildAppPath = (path: string, params?: Record<string, string>) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  if (!params || !Object.keys(params).length) {
    return normalizedPath
  }

  const searchParams = new URLSearchParams(params)
  return `${normalizedPath}?${searchParams.toString()}`
}
