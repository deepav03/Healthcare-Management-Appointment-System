import { request } from './client'

export const getDashboard = (role) => request(`/api/dashboard/${role.toLowerCase()}`)
export const getNotifications = () => request('/api/notifications')
export const markNotificationRead = (id) => request(`/api/notifications/${id}/read`, { method: 'PATCH' })
export const markAllNotificationsRead = () => request('/api/notifications/read-all', { method: 'PATCH' })
