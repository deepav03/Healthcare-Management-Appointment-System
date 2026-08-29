import { request } from './client'

export const getSchedules = (doctorId) => request(`/api/doctors/${doctorId}/schedules`)
export const createSchedule = (doctorId, payload) => request(`/api/doctors/${doctorId}/schedules`, { method: 'POST', body: JSON.stringify(payload) })
export const updateSchedule = (scheduleId, payload) => request(`/api/schedules/${scheduleId}`, { method: 'PATCH', body: JSON.stringify(payload) })
export const deleteSchedule = (scheduleId) => request(`/api/schedules/${scheduleId}`, { method: 'DELETE' })
export const getWeeklyAvailability = (doctorId) => request(`/api/doctors/${doctorId}/availability`)
export const getDailyAvailability = (doctorId, date) => request(`/api/doctors/${doctorId}/availability/${date}`)
