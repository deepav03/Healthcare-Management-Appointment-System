import { request } from './client'

export const getMyPatientProfile = () => request('/api/patients/me')
export const getPatients = (params = {}) => request(`/api/patients?${new URLSearchParams(params)}`)
export const getPatient = (id) => request(`/api/patients/${id}`)
export const updatePatient = (id, payload) => request(`/api/patients/${id}`, { method: 'PATCH', body: JSON.stringify(payload) })
