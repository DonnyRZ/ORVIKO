const normalizeBaseUrl = (value: string | undefined) => {
  if (!value) return ''
  return value.endsWith('/') ? value.slice(0, -1) : value
}

const API_BASE_URL = normalizeBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL)

const buildUrlWithParams = (base: string, params?: Record<string, string>) => {
  if (!params || !Object.keys(params).length) {
    return base
  }

  const searchParams = new URLSearchParams(params)
  return `${base}?${searchParams.toString()}`
}

export const buildApiUrl = (path: string) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return API_BASE_URL ? `${API_BASE_URL}${normalizedPath}` : normalizedPath
}

export const buildAuthUrl = (path: string, params?: Record<string, string>) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  const authBase = API_BASE_URL ? `${API_BASE_URL}${normalizedPath}` : normalizedPath
  return buildUrlWithParams(authBase, params)
}

export const buildAppPath = (path: string, params?: Record<string, string>) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return buildUrlWithParams(normalizedPath, params)
}
