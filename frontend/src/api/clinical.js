import { request } from './client'

export const getMedicalRecords = () => request('/api/medical-records')
export const getPatientMedicalRecords = (id) => request(`/api/patients/${id}/medical-records`)
export const createMedicalRecord = (payload) => request('/api/medical-records', { method: 'POST', body: JSON.stringify(payload) })
export const getPrescriptions = () => request('/api/prescriptions')
export const getPatientPrescriptions = (id) => request(`/api/patients/${id}/prescriptions`)
export const createPrescription = (payload) => request('/api/prescriptions', { method: 'POST', body: JSON.stringify(payload) })
