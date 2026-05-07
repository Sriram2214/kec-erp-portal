import { useState, useEffect } from 'react'
import api from '../../api/index'
import { useMaster } from '../../context/MasterContext'
import { Calendar, Clock, MapPin, Plus, Trash2, Search, X } from 'lucide-react'
import '../Students/Students.css' // Reuse base styles

export default function ExamSchedule() {
  const [schedules, setSchedules] = useState([])
  const [courses, setCourses] = useState([])
  const { master } = useMaster()
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({ course_id: '', exam_date: '', session: 'FN', venue: 'Main Hall' })
  const [saving, setSaving] = useState(false)
  const [search, setSearch] = useState('')

  const load = async () => {
    setLoading(true)
    try {
      const [resS, resC] = await Promise.all([
        api.get('/schedules'),
        api.get('/courses')
      ])
      setSchedules(resS.data)
      setCourses(resC.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleAdd = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.post('/schedules', form)
      setShowAdd(false)
      setForm({ course_id: '', exam_date: '', session: 'FN', venue: 'Main Hall' })
      load()
    } catch (e) {
      alert(e.response?.data?.message || 'Failed to add schedule')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this schedule?')) return
    try {
      await api.delete(`/schedules/${id}`)
      load()
    } catch (e) {
      alert('Failed to delete')
    }
  }

  const filtered = schedules.filter(s => 
    s.course_code.toLowerCase().includes(search.toLowerCase()) ||
    s.course_title.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="fade-in" style={{ paddingBottom: '5rem' }}>
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Examination</div>
        <div className="page-title">Exam Schedule</div>
        <div className="page-sub">Manage examination dates, sessions and venues</div>
      </div>

      <div className="filter-bar card">
        <div className="filter-row">
          <div className="search-wrap" style={{ flex: 1 }}>
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
            <Plus size={18} /> Create Schedule
          </button>
        </div>
      </div>

      {showAdd && (
        <div className="modal-overlay">
          <div className="card modal-content" style={{ maxWidth: '500px' }}>
            <div className="modal-header">
              <h3>Create New Schedule</h3>
              <button className="close-btn" onClick={() => setShowAdd(false)}><X size={20} /></button>
            </div>
            <form onSubmit={handleAdd} className="form-grid" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="field">
                <label>Course</label>
                <select required value={form.course_id} onChange={e => setForm({...form, course_id: e.target.value})}>
                  <option value="">Select Course</option>
                  {courses.map(c => (
                    <option key={c.id} value={c.id}>{c.course_code} - {c.course_title} ({c.batch})</option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label>Exam Date</label>
                <input type="date" required value={form.exam_date} onChange={e => setForm({...form, exam_date: e.target.value})} />
              </div>
              <div className="field">
                <label>Session</label>
                <select value={form.session} onChange={e => setForm({...form, session: e.target.value})}>
                  <option value="FN">Forenoon (FN)</option>
                  <option value="AN">Afternoon (AN)</option>
                </select>
              </div>
              <div className="field">
                <label>Venue</label>
                <input placeholder="Main Hall / Lab 1" value={form.venue} onChange={e => setForm({...form, venue: e.target.value})} />
              </div>
              <div className="form-actions">
                <button type="submit" className="btn btn-gold" disabled={saving}>
                  {saving ? 'Creating...' : 'Add to Schedule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="schedule-list card" style={{ marginTop: '1.5rem', padding: 0 }}>
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>Loading schedules...</div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: '#666' }}>No exam schedules found.</div>
        ) : (
          <table className="ese-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Course</th>
                <th>Session</th>
                <th>Venue</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(s => (
                <tr key={s.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <Calendar size={16} className="text-gold" />
                      <strong>{new Date(s.exam_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}</strong>
                    </div>
                  </td>
                  <td>
                    <div className="mono" style={{ fontWeight: 600 }}>{s.course_code}</div>
                    <div style={{ fontSize: '0.85rem', color: '#666' }}>{s.course_title}</div>
                  </td>
                  <td>
                    <div className={`badge ${s.session === 'FN' ? 'badge-blue' : 'badge-gold'}`} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', width: 'fit-content' }}>
                      <Clock size={12} /> {s.session}
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <MapPin size={14} style={{ opacity: 0.6 }} /> {s.venue || 'N/A'}
                    </div>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <button className="btn btn-red btn-sm" onClick={() => handleDelete(s.id)} title="Delete Schedule">
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
