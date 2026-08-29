import { useState } from 'react'
import { Activity, Bell, CalendarDays, CheckCircle2, ChevronDown, Clock3, FileText, LayoutDashboard, Menu, MoreHorizontal, Plus, Search, Settings, Stethoscope, Users, X } from 'lucide-react'
import './App.css'

const appointments = [
  { time: '09:00', name: 'Olivia Bennett', type: 'Annual physical', doctor: 'Dr. Maya Patel', status: 'Checked in', color: 'mint', initials: 'OB' },
  { time: '09:30', name: 'Noah Williams', type: 'Follow-up visit', doctor: 'Dr. James Chen', status: 'In 15 min', color: 'blue', initials: 'NW' },
  { time: '10:15', name: 'Emma Thompson', type: 'Dermatology consult', doctor: 'Dr. Maya Patel', status: 'In 1 hr', color: 'peach', initials: 'ET' },
  { time: '11:00', name: 'Liam Anderson', type: 'Medication review', doctor: 'Dr. Aiden Ross', status: 'In 2 hrs', color: 'lavender', initials: 'LA' },
]

const navItems = [
  { label: 'Overview', icon: LayoutDashboard },
  { label: 'Appointments', icon: CalendarDays },
  { label: 'Patients', icon: Users },
  { label: 'Clinical notes', icon: FileText },
]

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [activeNav, setActiveNav] = useState('Appointments')
  const [search, setSearch] = useState('')
  const [booked, setBooked] = useState(false)
  const visibleAppointments = appointments.filter((appointment) => `${appointment.name} ${appointment.type} ${appointment.doctor}`.toLowerCase().includes(search.toLowerCase()))

  function handleBooking(event) {
    event.preventDefault()
    setBooked(true)
    setTimeout(() => { setIsModalOpen(false); setBooked(false) }, 1200)
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark"><Activity size={18} strokeWidth={2.5} /></div><span>nurture<span className="brand-dot">.</span></span></div>
        <div className="practice-switcher"><div className="practice-avatar">MP</div><div><strong>Maplewood Clinic</strong><span>Primary care</span></div><ChevronDown size={15} /></div>
        <nav className="nav-list" aria-label="Main navigation"><p className="nav-label">Workspace</p>{navItems.map(({ label, icon: Icon }) => <button className={`nav-item ${activeNav === label ? 'active' : ''}`} key={label} onClick={() => setActiveNav(label)}><Icon size={18} /><span>{label}</span>{label === 'Appointments' && <span className="nav-count">8</span>}</button>)}<p className="nav-label secondary-label">Manage</p><button className="nav-item" onClick={() => setActiveNav('Team')}><Stethoscope size={18} /><span>Care team</span></button><button className="nav-item" onClick={() => setActiveNav('Settings')}><Settings size={18} /><span>Settings</span></button></nav>
        <div className="sidebar-bottom"><div className="help-card"><div className="help-icon">?</div><div><strong>Need a hand?</strong><span>Visit the help center</span></div></div><div className="user-row"><div className="user-avatar">JL</div><div><strong>Jordan Lee</strong><span>Administrator</span></div><MoreHorizontal size={18} /></div></div>
      </aside>
      <main className="main-content">
        <header className="topbar"><button className="mobile-menu" aria-label="Open menu"><Menu size={21} /></button><div className="breadcrumb"><span>Workspace</span><span>/</span><strong>{activeNav}</strong></div><div className="top-actions"><button className="icon-button" aria-label="Notifications"><Bell size={19} /><i /></button><div className="top-avatar">JL</div></div></header>
        <div className="content-wrap">
          <section className="page-intro"><div><p className="eyebrow">Wednesday, August 28, 2026</p><h1>Good morning, Jordan <span>✦</span></h1><p className="subheading">Here&apos;s what&apos;s happening at Maplewood Clinic today.</p></div><button className="primary-button" onClick={() => setIsModalOpen(true)}><Plus size={18} /> Book appointment</button></section>
          <section className="metrics-grid" aria-label="Daily summary"><div className="metric-card"><div className="metric-icon green"><CalendarDays size={19} /></div><div><span>Today&apos;s appointments</span><strong>24</strong><small className="positive">↑ 12% <em>vs. last week</em></small></div></div><div className="metric-card"><div className="metric-icon yellow"><Clock3 size={19} /></div><div><span>Average wait time</span><strong>12 <small>min</small></strong><small className="positive">↓ 4 min <em>vs. last week</em></small></div></div><div className="metric-card"><div className="metric-icon coral"><Users size={19} /></div><div><span>Patients seen</span><strong>16</strong><small className="neutral">of 24 scheduled</small></div></div><div className="metric-card"><div className="metric-icon blue"><CheckCircle2 size={19} /></div><div><span>Completion rate</span><strong>87<span className="percent">%</span></strong><small className="positive">↑ 3% <em>vs. last week</em></small></div></div></section>
          <section className="content-grid"><div className="appointments-panel"><div className="section-heading"><div><h2>Today&apos;s schedule</h2><p>Thursday, August 28 <span>·</span> 8 appointments</p></div><button className="text-button">View calendar <span>→</span></button></div><div className="schedule-toolbar"><div className="search-field"><Search size={17} /><input aria-label="Search appointments" placeholder="Search patient or provider" value={search} onChange={(event) => setSearch(event.target.value)} /></div><button className="filter-button">All providers <ChevronDown size={15} /></button></div><div className="appointment-list">{visibleAppointments.map((appointment) => <article className="appointment-row" key={appointment.name}><time>{appointment.time}</time><div className={`patient-avatar ${appointment.color}`}>{appointment.initials}</div><div className="appointment-details"><strong>{appointment.name}</strong><span>{appointment.type} <i>·</i> {appointment.doctor}</span></div><span className={`status-pill ${appointment.status === 'Checked in' ? 'checked' : ''}`}>{appointment.status}</span><button className="more-button" aria-label={`More options for ${appointment.name}`}><MoreHorizontal size={18} /></button></article>)}{visibleAppointments.length === 0 && <div className="empty-state">No appointments match your search.</div>}</div><button className="schedule-footer">Show all appointments <span>8 total</span><ChevronDown size={16} /></button></div>
            <aside className="right-column"><div className="insight-card"><div className="insight-top"><div className="pulse-icon"><Activity size={18} /></div><span>Clinic pulse</span><button aria-label="More clinic pulse options"><MoreHorizontal size={18} /></button></div><h3>Running smoothly</h3><p>Your schedule is 8% ahead of the clinic average today.</p><div className="progress-bar"><span /></div><div className="progress-labels"><span>Patient flow</span><strong>Good</strong></div></div><div className="team-card"><div className="section-heading compact"><div><h2>Care team</h2><p>4 providers on duty</p></div><button className="more-button" aria-label="More care team options"><MoreHorizontal size={18} /></button></div><div className="team-list"><div className="team-member"><div className="provider-avatar teal">MP</div><div><strong>Dr. Maya Patel</strong><span>General medicine</span></div><i className="online" /></div><div className="team-member"><div className="provider-avatar pink">JC</div><div><strong>Dr. James Chen</strong><span>Family medicine</span></div><i className="online" /></div><div className="team-member"><div className="provider-avatar gold">AR</div><div><strong>Dr. Aiden Ross</strong><span>Pediatrics</span></div><i className="online" /></div></div><button className="team-footer">View care team <span>→</span></button></div></aside></section>
        </div>
      </main>
      {isModalOpen && <div className="modal-backdrop" onClick={() => setIsModalOpen(false)}><div className="booking-modal" role="dialog" aria-modal="true" aria-labelledby="booking-title" onClick={(event) => event.stopPropagation()}><div className="modal-header"><div><p className="eyebrow">New appointment</p><h2 id="booking-title">Book a visit</h2></div><button className="close-button" aria-label="Close booking dialog" onClick={() => setIsModalOpen(false)}><X size={19} /></button></div><form onSubmit={handleBooking}><label>Patient<input required placeholder="Search patient name" /></label><label>Provider<select defaultValue="maya"><option value="maya">Dr. Maya Patel</option><option value="chen">Dr. James Chen</option><option value="ross">Dr. Aiden Ross</option></select></label><div className="form-row"><label>Date<input required type="date" defaultValue="2026-08-28" /></label><label>Time<select defaultValue="1030"><option value="1030">10:30 AM</option><option value="1100">11:00 AM</option><option value="1130">11:30 AM</option></select></label></div><label>Visit type<select defaultValue="follow"><option value="follow">Follow-up visit</option><option value="annual">Annual physical</option><option value="consult">Consultation</option></select></label><button className="primary-button modal-submit" type="submit">{booked ? <><CheckCircle2 size={18} /> Appointment booked</> : <><CalendarDays size={18} /> Confirm appointment</>}</button></form></div></div>}
    </div>
  )
}

export default App