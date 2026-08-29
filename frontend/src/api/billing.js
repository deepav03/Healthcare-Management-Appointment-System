import { request } from './client'

export const getBills = () => request('/api/bills')
export const getBill = (id) => request(`/api/bills/${id}`)
export const getPatientBills = (id) => request(`/api/patients/${id}/bills`)
export const createBill = (payload) => request('/api/bills', { method: 'POST', body: JSON.stringify(payload) })
export const getPayments = () => request('/api/payments')
export const getPayment = (id) => request(`/api/payments/${id}`)
export const createPayment = (payload) => request('/api/payments', { method: 'POST', body: JSON.stringify(payload) })
