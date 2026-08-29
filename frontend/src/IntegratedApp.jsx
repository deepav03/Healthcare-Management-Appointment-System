import { useEffect, useState } from 'react'
import { Activity, Bell, CalendarDays, CheckCircle2, LogOut, Search, Users } from 'lucide-react'
import { currentUser, login, logout, register } from './api/auth'
import { createAppointment, getAppointments, getMyAppointments } from './api/appointments'
import { getDashboard, getNotifications, markAllNotificationsRead, markNotificationRead } from './api/dashboard'
import { getDoctorAvailability, getDoctors } from './api/doctors'
import { clearStoredToken, getStoredToken } from './api/client'
import './App.css'

const today = new Date().toISOString().slice(0, 10)

function LoginScreen({ onAuthenticated }) {
  const [isRegistering, setIsRegistering] = useState(false)
  const [form, setForm] = useState({ email: '', password: '', first_name: '', last_name: '', phone: '', password_confirmation: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (isRegistering) {
        await register(form)
        setIsRegistering(false)
        setError('Account created. Sign in to continue.')
      } else {
        onAuthenticated(await login(form.email, form.password))
      }
    } catch (requestError) {
      setError(requestError.message)
    } finally { setLoading(false) }
  }

  function update(field, value) { setForm((current) => ({ ...current, [field]: value })) }

  return <main className="auth-screen"><div className="auth-panel"><div className="brand"><div className="brand-mark"><Activity size={18} strokeWidth={2.5} /></div><span>nurture<span className="brand-dot">.</span></span></div><p className="eyebrow">Maplewood Clinic</p><h1>{isRegistering ? 'Create your patient account' : 'Welcome back'}</h1><p className="subheading">{isRegistering ? 'Your care journey starts here.' : 'Sign in to your care workspace.'}</p>{error && <div className="form-error" role="alert">{error}</div>}<form onSubmit={submit}>{isRegistering && <><label>First name<input data-testid="registration-first-name" required value={form.first_name} onChange={(event) => update('first_name', event.target.value)} /></label><label>Last name<input data-testid="registration-last-name" required value={form.last_name} onChange={(event) => update('last_name', event.target.value)} /></label><label>Phone<input data-testid="registration-phone" required value={form.phone} onChange={(event) => update('phone', event.target.value)} /></label></>}<label>Email<input data-testid={isRegistering ? 'registration-email' : 'login-email'} type="email" required value={form.email} onChange={(event) => update('email', event.target.value)} /></label><label>Password<input data-testid={isRegistering ? 'registration-password' : 'login-password'} type="password" required value={form.password} onChange={(event) => update('password', event.target.value)} /></label>{isRegistering && <label>Confirm password<input data-testid="registration-password-confirmation" type="password" required value={form.password_confirmation} onChange={(event) => update('password_confirmation', event.target.value)} /></label>}<button className="primary-button modal-submit" data-testid={isRegistering ? 'registration-submit' : 'login-button'} disabled={loading}>{loading ? 'Connecting...' : isRegistering ? 'Create account' : 'Sign in'}</button></form><button className="text-button auth-switch" onClick={() => { setIsRegistering(!isRegistering); setError('') }}>{isRegistering ? 'Already have an account? Sign in' : 'New patient? Create an account'}</button></div></main>
}

function IntegratedApp() {
  const [user, setUser] = useState(null)
  const [dashboard, setDashboard] = useState(null)
  const [appointments, setAppointments] = useState([])
  const [doctors, setDoctors] = useState([])
  const [notifications, setNotifications] = useState([])
  const [search, setSearch] = useState('')
  const [selectedDoctor, setSelectedDoctor] = useState(null)
  const [availability, setAvailability] = useState(null)
  const [booking, setBooking] = useState({ date: today, time: '', reason: '' })
  const [notice, setNotice] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!getStoredToken()) return
    currentUser().then((nextUser) => { setUser(nextUser); return loadWorkspace(nextUser) }).catch(() => clearStoredToken())
  }, [])

  async function loadWorkspace(nextUser = user) {
    if (!nextUser) return
    setLoading(true); setError('')
    try {
      const role = nextUser.role.toLowerCase()
      const [summary, doctorList, notificationList] = await Promise.all([getDashboard(role), getDoctors(), getNotifications()])
      const appointmentResult = role === 'admin' ? await getAppointments() : await getMyAppointments()
      setDashboard(summary.data); setDoctors(doctorList); setNotifications(notificationList); setAppointments(appointmentResult.appointments)
    } catch (requestError) { setError(requestError.message) } finally { setLoading(false) }
  }

  async function authenticated(nextUser) { setUser(nextUser); await loadWorkspace(nextUser) }

  async function chooseDoctor(doctor) {
    setSelectedDoctor(doctor); setAvailability(null); setError('')
    try { setAvailability(await getDoctorAvailability(doctor.id, booking.date)) } catch (requestError) { setError(requestError.message) }
  }

  async function updateDate(value) {
    setBooking((current) => ({ ...current, date: value, time: '' }))
    if (selectedDoctor) {
      try { setAvailability(await getDoctorAvailability(selectedDoctor.id, value)) } catch (requestError) { setError(requestError.message) }
    }
  }

  async function submitBooking(event) {
    event.preventDefault(); setError(''); setNotice('')
    try {
      await createAppointment({ doctor_id: selectedDoctor.id, appointment_date: booking.date, appointment_time: booking.time, reason: booking.reason })
      setNotice('Appointment requested successfully.'); setSelectedDoctor(null); await loadWorkspace()
    } catch (requestError) { setError(requestError.message) }
  }

  async function signOut() { await logout(); clearStoredToken(); setUser(null); setDashboard(null) }
  async function readNotification(id) { await markNotificationRead(id); setNotifications((items) => items.map((item) => item.id === id ? { ...item, read_status: true } : item)) }
  async function readAll() { await markAllNotificationsRead(); setNotifications((items) => items.map((item) => ({ ...item, read_status: true }))) }

  if (!user) return <LoginScreen onAuthenticated={authenticated} />
  const role = user.role.toLowerCase()
  const visibleDoctors = doctors.filter((doctor) => `${doctor.first_name} ${doctor.last_name} ${doctor.specialization}`.toLowerCase().includes(search.toLowerCase()))
  const metrics = role === 'admin' ? [['Patients', dashboard?.total_patients], ['Doctors', dashboard?.total_doctors], ['Today', dashboard?.today_appointments], ['Revenue', dashboard?.total_revenue]] : role === 'doctor' ? [['Today', dashboard?.today_appointments], ['Upcoming', dashboard?.upcoming_appointments], ['Completed', dashboard?.completed_appointments], ['Patients', dashboard?.patient_count]] : [['Appointments', dashboard?.appointment_count], ['Records', dashboard?.medical_record_count], ['Prescriptions', dashboard?.prescription_count], ['Unread', dashboard?.unread_notification_count]]

  return <div className="app-shell"><aside className="sidebar"><div className="brand"><div className="brand-mark"><Activity size={18} strokeWidth={2.5} /></div><span>nurture<span className="brand-dot">.</span></span></div><div className="practice-switcher"><div className="practice-avatar">MP</div><div><strong>Maplewood Clinic</strong><span>{user.role}</span></div></div><nav className="nav-list"><p className="nav-label">Workspace</p><button className="nav-item active"><CalendarDays size={18} /><span>Dashboard</span></button><button className="nav-item"><Users size={18} /><span>People</span></button><button className="nav-item"><Bell size={18} /><span>Notifications</span>{notifications.some((item) => !item.read_status) && <span className="nav-count">{notifications.filter((item) => !item.read_status).length}</span>}</button></nav><div className="sidebar-bottom"><button className="nav-item" onClick={signOut}><LogOut size={18} /><span>Sign out</span></button><div className="user-row"><div className="user-avatar">{user.first_name[0]}{user.last_name[0]}</div><div><strong>{user.first_name} {user.last_name}</strong><span>{user.role}</span></div></div></div></aside><main className="main-content"><header className="topbar"><div className="breadcrumb"><span>Workspace</span><span>/</span><strong>Dashboard</strong></div><div className="top-actions"><button className="icon-button" aria-label="Notifications"><Bell size={19} /></button><div className="top-avatar">{user.first_name[0]}{user.last_name[0]}</div></div></header><div className="content-wrap"><section className="page-intro"><div><p className="eyebrow">Live care workspace</p><h1>Good morning, {user.first_name} <span>✦</span></h1><p className="subheading">{role === 'patient' ? 'Your appointments and care, in one place.' : 'Here is what is happening at Maplewood Clinic today.'}</p></div>{role === 'patient' && <button className="primary-button" data-testid="book-appointment" onClick={() => document.getElementById('doctor-search')?.focus()}><CalendarDays size={18} /> Find a doctor</button>}</section>{notice && <div className="success-banner" role="status"><CheckCircle2 size={17} />{notice}</div>}{error && <div className="form-error" role="alert">{error}</div>}<section className="metrics-grid" aria-label="Live dashboard metrics">{metrics.map(([label, value], index) => <div className="metric-card" data-testid="dashboard-card" key={label}><div className={`metric-icon ${['green', 'yellow', 'coral', 'blue'][index]}`}><CalendarDays size={19} /></div><div><span>{label}</span><strong>{value ?? (loading ? '...' : '0')}</strong><small className="neutral">Live from API</small></div></div>)}</section><section className="content-grid"><div className="appointments-panel"><div className="section-heading"><div><h2>{role === 'patient' ? 'My appointments' : 'Appointment schedule'}</h2><p>{appointments.length} appointments from FastAPI</p></div></div><div className="appointment-list">{appointments.map((appointment) => <article className="appointment-row" data-testid="appointment-item" key={appointment.id}><time>{appointment.appointment_time.slice(0, 5)}</time><div className="patient-avatar mint"><CalendarDays size={15} /></div><div className="appointment-details"><strong>{role === 'doctor' ? appointment.patient_name : appointment.doctor_name}</strong><span>{appointment.appointment_date} <i>·</i> {appointment.reason || 'Consultation'}</span></div><span className="status-pill checked">{appointment.status}</span></article>)}{!appointments.length && <div className="empty-state">No appointments yet.</div>}</div></div><aside className="right-column"><div className="team-card"><div className="section-heading compact"><div><h2>Find care</h2><p>Active providers from API</p></div></div><div className="schedule-toolbar"><div className="search-field"><Search size={17} /><input id="doctor-search" data-testid="doctor-search" aria-label="Search doctors" placeholder="Search specialty or doctor" value={search} onChange={(event) => setSearch(event.target.value)} /></div></div><div className="team-list">{visibleDoctors.slice(0, 5).map((doctor) => <button className="team-member doctor-choice" data-testid="doctor-card" key={doctor.id} onClick={() => chooseDoctor(doctor)}><div className="provider-avatar teal">{doctor.first_name[0]}{doctor.last_name[0]}</div><div><strong>Dr. {doctor.first_name} {doctor.last_name}</strong><span>{doctor.specialization}</span></div></button>)}</div></div><div className="insight-card"><div className="insight-top"><div className="pulse-icon"><Bell size={18} /></div><span>Notifications</span><button className="text-button" onClick={readAll}>Read all</button></div>{notifications.slice(0, 3).map((item) => <button className={`notification-line ${item.read_status ? '' : 'unread'}`} data-testid="notification-item" key={item.id} onClick={() => readNotification(item.id)}><strong>{item.notification_type.replaceAll('_', ' ')}</strong><span>{item.message}</span></button>)}{!notifications.length && <p>No notifications yet.</p>}</div></aside></section></div></main>{selectedDoctor && <div className="modal-backdrop" onClick={() => setSelectedDoctor(null)}><div className="booking-modal" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}><div className="modal-header"><div><p className="eyebrow">{selectedDoctor.specialization}</p><h2>Book with Dr. {selectedDoctor.first_name} {selectedDoctor.last_name}</h2></div><button className="close-button" onClick={() => setSelectedDoctor(null)}>×</button></div><form onSubmit={submitBooking}><label>Date<input data-testid="appointment-date" required type="date" min={today} value={booking.date} onChange={(event) => updateDate(event.target.value)} /></label><label>Available slot<select data-testid="appointment-slot" required value={booking.time} onChange={(event) => setBooking((current) => ({ ...current, time: event.target.value }))}><option value="">Select a slot</option>{availability?.available_slots?.map((slot) => <option value={`${slot}:00`} key={slot}>{slot}</option>)}</select></label><label>Reason<textarea value={booking.reason} onChange={(event) => setBooking((current) => ({ ...current, reason: event.target.value }))} /></label><button className="primary-button modal-submit" data-testid="book-appointment" disabled={!availability?.available_slots?.length}><CalendarDays size={18} /> Request appointment</button></form></div></div>}</div>
}

export default IntegratedApp
