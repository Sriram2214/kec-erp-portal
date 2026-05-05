import { useEffect, useState } from 'react'
import api from '../../api/index'
import '../Students/Students.css'

const EMPTY = { course_code: '', course_title: '', department: '', credits: 3 }

export default function Courses() {
  const [courses, setCourses] = useState([])
  const [master,  setMaster]  = useState({ departments: [] })
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form,    setForm]    = useState(EMPTY)
  const [saving,  setSaving]  = useState(false)
  const [err,     setErr]     = useState('')
  const [search,  setSearch]  = useState('')

  const load = () => {
    setLoading(true)
    api.get('/courses').then(r => setCourses(r.data)).finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
    api.get('/master').then(r => setMaster(r.data))
  }, [])

  const filtered = courses.filter(c => 
    c.course_title.toLowerCase().includes(search.toLowerCase()) ||
    c.course_code.toLowerCase().includes(search.toLowerCase())
  )

  const handleSubmit = async e => {
    e.preventDefault()
    setErr(''); setSaving(true)
    try {
      await api.post('/courses', form)
      setShowForm(false); setForm(EMPTY); load()
    } catch(ex) {
      setErr(ex.response?.data?.message || 'Failed to add course')
    } finally { setSaving(false) }
  }

  const handleDelete = async (id, code) => {
    if (!confirm(`Delete course ${code}?`)) return
    await api.delete(`/courses/${id}`); load()
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Courses</div>
        <div className="page-title">Course Management</div>
        <div className="page-sub">Manage Subjects, Credits & Department Mapping</div>
      </div>

      {showForm && (
        <div className="card form-card">
          <div className="card-title">Add New Course</div>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="field">
                <label>Course Code</label>
                <input required placeholder="e.g. CS3401" value={form.course_code} onChange={e => setForm({...form, course_code: e.target.value})} />
              </div>
              <div className="field">
                <label>Course Title</label>
                <input required placeholder="e.g. Data Structures" value={form.course_title} onChange={e => setForm({...form, course_title: e.target.value})} />
              </div>
              <div className="field">
                <label>Department</label>
                <select value={form.department} onChange={e => setForm({...form, department: e.target.value})}>
                  <option value="">Common / All</option>
                  {master.departments.map(d => <option key={d.id} value={d.code}>{d.code}</option>)}
                </select>
              </div>
              <div className="field">
                <label>Credits</label>
                <input type="number" min="0" max="10" value={form.credits} onChange={e => setForm({...form, credits: e.target.value})} />
              </div>
            </div>
            {err && <div className="alert-error">{err}</div>}
            <div className="form-actions">
              <button type="submit" className="btn btn-gold" disabled={saving}>{saving ? 'Saving…' : 'Add Course'}</button>
              <button type="button" className="btn btn-outline" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="filter-bar card">
        <div className="filter-row">
          <input className="search-input" placeholder="Search title / code…" value={search} onChange={e => setSearch(e.target.value)} />
          {!showForm && <button className="btn btn-gold btn-sm" onClick={() => setShowForm(true)}>+ Add Course</button>}
        </div>
      </div>

      <div className="card">
        {loading ? <div className="loading-row">Loading…</div> : (
          <table>
            <thead>
              <tr>
                <th>Code</th>
                <th>Title</th>
                <th>Department</th>
                <th>Credits</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(c => (
                <tr key={c.id}>
                  <td className="mono"><strong>{c.course_code}</strong></td>
                  <td>{c.course_title}</td>
                  <td><span className="badge badge-blue">{c.department || 'Common'}</span></td>
                  <td>{c.credits}</td>
                  <td>
                    <button className="btn btn-red btn-sm" onClick={() => handleDelete(c.id, c.course_code)}>Delete</button>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && <tr><td colSpan="5" className="empty-row">No courses found.</td></tr>}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
