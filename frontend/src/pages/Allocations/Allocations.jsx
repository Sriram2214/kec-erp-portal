import { useEffect, useState } from 'react'
import api from '../../api/index'
import '../Students/Students.css'

const EMPTY = { faculty_id: '', course_id: '', batch: '', academic_year_id: '', section: 'A' }

export default function Allocations() {
  const [allocs, setAllocs] = useState([])
  const [master, setMaster] = useState({ departments: [], batches: [], academic_years: [] })
  const [faculty, setFaculty] = useState([])
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY)
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')

  const loadData = async () => {
    setLoading(true)
    try {
      const [a, m, f, c] = await Promise.all([
        api.get('/allocations'),
        api.get('/master'),
        api.get('/faculty'),
        api.get('/courses')
      ])
      setAllocs(a.data)
      setMaster(m.data)
      setFaculty(f.data)
      setCourses(c.data)
    } catch (ex) {}
    finally { setLoading(false) }
  }

  useEffect(() => { loadData() }, [])

  const handleSubmit = async e => {
    e.preventDefault()
    setErr(''); setSaving(true)
    try {
      await api.post('/allocations', form)
      setShowForm(false); setForm(EMPTY); loadData()
    } catch(ex) {
      setErr(ex.response?.data?.message || 'Failed to create allocation')
    } finally { setSaving(false) }
  }

  const handleDelete = async (id) => {
    if (!confirm(`Remove this allocation?`)) return
    await api.delete(`/allocations/${id}`); loadData()
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Allocations</div>
        <div className="page-title">Faculty-Course Mapping</div>
        <div className="page-sub">Assign Faculty to Subjects, Batches & Sections (Item 8a)</div>
      </div>

      {showForm && (
        <div className="card form-card">
          <div className="card-title">New Mapping</div>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="field">
                <label>Faculty Member</label>
                <select required value={form.faculty_id} onChange={e => setForm({...form, faculty_id: e.target.value})}>
                  <option value="">Select Faculty</option>
                  {faculty.map(f => <option key={f.id} value={f.id}>{f.name} ({f.department})</option>)}
                </select>
              </div>
              <div className="field">
                <label>Course / Subject</label>
                <select required value={form.course_id} onChange={e => setForm({...form, course_id: e.target.value})}>
                  <option value="">Select Course</option>
                  {courses.map(c => <option key={c.id} value={c.id}>{c.course_code} — {c.course_title}</option>)}
                </select>
              </div>
              <div className="field">
                <label>Batch</label>
                <select required value={form.batch} onChange={e => setForm({...form, batch: e.target.value})}>
                  <option value="">Select Batch</option>
                  {master.batches.map(b => <option key={b.id} value={b.label}>{b.label}</option>)}
                </select>
              </div>
              <div className="field">
                <label>Section</label>
                <input required placeholder="e.g. A" value={form.section} onChange={e => setForm({...form, section: e.target.value})} />
              </div>
              <div className="field">
                <label>Academic Year</label>
                <select required value={form.academic_year_id} onChange={e => setForm({...form, academic_year_id: e.target.value})}>
                  <option value="">Select Year</option>
                  {master.academic_years.map(ay => <option key={ay.id} value={ay.id}>{ay.label} ({ay.semester})</option>)}
                </select>
              </div>
            </div>
            {err && <div className="alert-error">{err}</div>}
            <div className="form-actions">
              <button type="submit" className="btn btn-gold" disabled={saving}>{saving ? 'Saving…' : 'Create Mapping'}</button>
              <button type="button" className="btn btn-outline" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="filter-bar card">
        {!showForm && <button className="btn btn-gold" onClick={() => setShowForm(true)}>+ New Allocation</button>}
      </div>

      <div className="card">
        {loading ? <div className="loading-row">Loading mappings…</div> : (
          <table>
            <thead>
              <tr>
                <th>Faculty</th>
                <th>Course</th>
                <th>Batch</th>
                <th>Section</th>
                <th>Academic Year</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {allocs.map(a => (
                <tr key={a.id}>
                  <td><strong>{a.faculty_name}</strong></td>
                  <td><span className="badge badge-blue">{a.course_code}</span> {a.course_title}</td>
                  <td>{a.batch}</td>
                  <td className="mono">{a.section}</td>
                  <td className="muted">{a.academic_year}</td>
                  <td>
                    <button className="btn btn-red btn-sm" onClick={() => handleDelete(a.id)}>Remove</button>
                  </td>
                </tr>
              ))}
              {allocs.length === 0 && <tr><td colSpan="6" className="empty-row">No mappings found.</td></tr>}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
