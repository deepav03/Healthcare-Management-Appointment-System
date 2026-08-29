import { request } from './client'

export const getMyAppointments = () => request('/api/appointments/my')
export const getAppointments = (params = {}) => request(`/api/appointments?${new URLSearchParams(params)}`)
export const createAppointment = (payload) => request('/api/appointments', { method: 'POST', body: JSON.stringify(payload) })
export const cancelAppointment = (id) => request(`/api/appointments/${id}/cancel`, { method: 'PATCH' })
export const rescheduleAppointment = (id, payload) => request(`/api/appointments/${id}/reschedule`, { method: 'PATCH', body: JSON.stringify(payload) })
export const updateAppointmentStatus = (id, status) => request(`/api/appointments/${id}/${status.toLowerCase()}`, { method: 'PATCH' })
