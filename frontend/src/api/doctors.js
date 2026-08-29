import { request } from './client'

export const getDoctors = (params = {}) => request(`/api/doctors?${new URLSearchParams(params)}`)
export const getDoctorAvailability = (id, date) => request(`/api/doctors/${id}/availability/${date}`)
export const getDoctorSchedules = (id) => request(`/api/doctors/${id}/schedules`)
