import { request } from './client'

export const getAppointmentReport = (params = {}) => request(`/api/reports/appointments?${new URLSearchParams(params)}`)
export const getRevenueReport = (params = {}) => request(`/api/reports/revenue?${new URLSearchParams(params)}`)
export const getPaymentReport = (params = {}) => request(`/api/reports/payments?${new URLSearchParams(params)}`)
export const getPatientReport = () => request('/api/reports/patients')
