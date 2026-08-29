import { clearStoredToken, request, setStoredToken } from './client'

export async function login(email, password) {
  const result = await request('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })
  setStoredToken(result.access_token)
  return request('/api/auth/me')
}

export function register(payload) {
  return request('/api/auth/register', { method: 'POST', body: JSON.stringify(payload) })
}

export function currentUser() {
  return request('/api/auth/me')
}

export async function logout() {
  try { await request('/api/auth/logout', { method: 'POST' }) } finally { clearStoredToken() }
}
