import { useState, useEffect } from 'react'
import api from '../../api/index'
import { useMaster } from '../../context/MasterContext'
import { useToast } from '../../components/Toast/Toast'
import { Calendar, Clock, MapPin, Plus, Trash2, Search, X, Check, AlertCircle } from 'lucide-react'
import { Skeleton } from '../../components/Skeleton/Skeleton'
import './ExamSchedule.css'

export default function ExamSchedule() {
  const [schedules, setSchedules] = useState([])
  const [courses, setCourses] = useState([])
  const { master, loading: masterLoading } = useMaster()
  const { addToast } = useToast()
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({ course_id: '', exam_date: '', session: 'FN', venue: 'Main Hall' })
  const [saving, setSaving] = useState(false)
  const [search, setSearch] = useState('')

  const loadSchedules = async () => {
    try {
      const res = await api.get('/schedules')
      setSchedules(res.data)
    } catch (e) {
      addToast('Failed to load exam schedules', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSchedules()
  }, [])

  // Courses are fetched by MasterContext in background
  const allCourses = master.courses || []

  const handleAdd = async (e) => {
    e.preventDefault()
    if (!form.course_id || !form.exam_date) return
    setSaving(true)
    try {
      await api.post('/schedules', form)
      addToast('Examination scheduled successfully!', 'success')
      setShowAdd(false)
      setForm({ course_id: '', exam_date: '', session: 'FN', venue: 'Main Hall' })
      loadSchedules()
    } catch (e) {
      addToast(e.response?.data?.message || 'Failed to schedule exam', 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this schedule? This may affect attendance records.')) return
    try {
      await api.delete(`/schedules/${id}`)
      addToast('Schedule deleted', 'info')
      loadSchedules()
    } catch (e) {
      addToast('Failed to delete schedule', 'error')
    }
  }

  const filtered = schedules.filter(s => 
    s.course_code?.toLowerCase().includes(search.toLowerCase()) ||
    s.course_title?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="fade-in exam-schedule-page">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › COE Command Center › Exam Schedule</div>
        <div className="page-title">Examination Timetable</div>
        <div className="page-sub">Configure end-semester examination dates and venues</div>
      </div>

      <div className="filter-bar card">
        <div className="filter-row">
          <div className="search-wrap">
            <div className="search-box">
              <Search size={18} />
              <input 
                placeholder="Search by course code or title..." 
                value={search} 
                onChange={e => setSearch(e.target.value)} 
              />
            </div>
          </div>
          <button className="btn btn-gold" onClick={() => setShowAdd(true)}>
            <Plus size={18} /> Create New Entry
          </button>
        </div>
      </div>

      {showAdd && (
        <div className="modal-overlay fade-in">
          <div className="card modal-content">
            <div className="modal-header">
              <div className="modal-title-wrap">
                <Calendar className="text-gold" size={24} />
                <h3>Schedule New Exam</h3>
              </div>
              <button className="close-icon-btn" onClick={() => setShowAdd(false)}><X size={20} /></button>
            </div>
            
            <form onSubmit={handleAdd} className="form-container">
              <div className="field">
                <label>Target Course</label>
                <select required value={form.course_id} onChange={e => setForm({...form, course_id: e.target.value})}>
                  <option value="">-- Search and Select Course --</option>
                  {allCourses.sort((a,b) => a.course_code.localeCompare(b.course_code)).map(c => (
                    <option key={c.id} value={c.id}>
                      {c.course_code} - {c.course_title} ({c.batch})
                    </option>
                  ))}
                </select>
                {allCourses.length === 0 && <p className="field-hint warning">Loading course directory...</p>}
              </div>

              <div className="form-row-2">
                <div className="field">
                  <label>Exam Date</label>
                  <input type="date" required value={form.exam_date} onChange={e => setForm({...form, exam_date: e.target.value})} />
                </div>
                <div className="field">
                  <label>Session</label>
                  <div className="session-toggle-premium">
                    <button 
                      type="button" 
                      className={form.session === 'FN' ? 'active' : ''} 
                      onClick={() => setForm({...form, session: 'FN'})}
                    >
                      FN <small>(10:00 - 01:00)</small>
                    </button>
                    <button 
                      type="button" 
                      className={form.session === 'AN' ? 'active' : ''} 
                      onClick={() => setForm({...form, session: 'AN'})}
                    >
                      AN <small>(02:00 - 05:00)</small>
                    </button>
                  </div>
                </div>
              </div>

              <div className="field">
                <label>Venue / Location</label>
                <div className="venue-input-wrap">
                  <MapPin size={18} />
                  <input placeholder="e.g. Main Hall, Drawing Hall, Lab 4" value={form.venue} onChange={e => setForm({...form, venue: e.target.value})} />
                </div>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-outline" onClick={() => setShowAdd(false)}>Cancel</button>
                <button type="submit" className="btn btn-gold" disabled={saving || allCourses.length === 0}>
                  {saving ? 'Scheduling...' : 'Save Schedule Entry'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="schedule-grid card-container">
        {loading ? (
          <div className="skeleton-container" style={{ padding: '2rem' }}>
            <Skeleton height="60px" style={{ marginBottom: '1rem' }} />
            <Skeleton height="60px" style={{ marginBottom: '1rem' }} />
            <Skeleton height="60px" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="empty-state-wrap">
            <AlertCircle size={48} className="text-muted" />
            <h3>No Schedules Found</h3>
            <p>Try adjusting your search or create a new examination entry.</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="premium-table">
              <thead>
                <tr>
                  <th>Examination Date</th>
                  <th>Course Information</th>
                  <th>Session</th>
                  <th>Venue</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(s => (
                  <tr key={s.id} className="table-row-hover">
                    <td className="date-cell">
                      <div className="date-badge">
                        <span className="day">{new Date(s.exam_date).getDate()}</span>
                        <span className="month">{new Date(s.exam_date).toLocaleDateString('en-US', { month: 'short' }).toUpperCase()}</span>
                      </div>
                      <div className="date-info">
                        <div className="year">{new Date(s.exam_date).getFullYear()}</div>
                        <div className="weekday">{new Date(s.exam_date).toLocaleDateString('en-US', { weekday: 'long' })}</div>
                      </div>
                    </td>
                    <td className="course-cell">
                      <div className="course-code-tag">{s.course_code}</div>
                      <div className="course-title-main">{s.course_title}</div>
                    </td>
                    <td>
                      <div className={`session-chip ${s.session}`}>
                        <Clock size={14} />
                        {s.session}
                      </div>
                    </td>
                    <td>
                      <div className="venue-chip">
                        <MapPin size={14} />
                        {s.venue || 'TBA'}
                      </div>
                    </td>
                    <td className="text-right">
                      <button className="delete-action-btn" onClick={() => handleDelete(s.id)}>
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
