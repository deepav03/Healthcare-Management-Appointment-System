import { request } from './client'

export const getNotifications = () => request('/api/notifications')
export const getNotification = (id) => request(`/api/notifications/${id}`)
export const markNotificationRead = (id) => request(`/api/notifications/${id}/read`, { method: 'PATCH' })
export const markAllNotificationsRead = () => request('/api/notifications/read-all', { method: 'PATCH' })
