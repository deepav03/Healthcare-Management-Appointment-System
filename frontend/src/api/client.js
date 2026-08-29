const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

export function getStoredToken() {
  return sessionStorage.getItem('healthcare_access_token')
}

export function setStoredToken(token) {
  sessionStorage.setItem('healthcare_access_token', token)
}

export function clearStoredToken() {
  sessionStorage.removeItem('healthcare_access_token')
}

export async function request(path, options = {}) {
  const headers = { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(options.headers || {}) }
  const token = getStoredToken()
  if (token) headers.Authorization = `Bearer ${token}`
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })
  let payload = null
  try { payload = await response.json() } catch { payload = null }
  if (!response.ok) {
    const error = new Error(payload?.detail || `Request failed (${response.status})`)
    error.status = response.status
    throw error
  }
  return payload
}

export { API_BASE_URL }
