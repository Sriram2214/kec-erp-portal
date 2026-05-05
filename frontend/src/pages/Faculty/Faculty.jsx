import { useEffect, useState } from 'react'
import api from '../../api/index'
import '../Students/Students.css'

const EMPTY = { employee_id: '', name: '', department: '', designation: '', email: '', phone: '' }

export default function Faculty() {
  const [faculty,  setFaculty]  = useState([])
  const [master,   setMaster]   = useState({ departments: [] })
  const [loading,  setLoading]  = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form,     setForm]     = useState(EMPTY)
  const [saving,   setSaving]   = useState(false)
  const [err,      setErr]      = useState('')
  const [success,  setSuccess]  = useState('')
  const [filterDept, setFilterDept] = useState('')
  const [search,     setSearch]     = useState('')

  const load = () => {
    setLoading(true)
    api.get('/faculty').then(r => setFaculty(r.data)).finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
    api.get('/master').then(r => setMaster(r.data))
  }, [])

  const filtered = faculty.filter(f => {
    if (filterDept && f.department !== filterDept) return false
    if (search && !f.name.toLowerCase().includes(search.toLowerCase()) &&
                  !f.employee_id.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  // Group by department
  const byDept = master.departments.reduce((acc, d) => {
    acc[d.code] = filtered.filter(f => f.department === d.code)
    return acc
  }, {})

  const handleSubmit = async e => {
    e.preventDefault()
    setErr(''); setSaving(true)
    try {
      await api.post('/faculty', form)
      setSuccess('Faculty added successfully!')
      setForm(EMPTY); setShowForm(false); load()
      setTimeout(() => setSuccess(''), 3000)
    } catch(ex) {
      setErr(ex.response?.data?.message || 'Failed to add faculty')
    } finally { setSaving(false) }
  }

  const handleDelete = async (id, name) => {
    if (!confirm(`Delete ${name}?`)) return
    await api.delete(`/faculty/${id}`); load()
  }

  const set = k => e => setForm(f => ({...f, [k]: e.target.value}))

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Faculty</div>
        <div className="page-title">Faculty</div>
        <div className="page-sub">Department-wise Faculty & Staff Records</div>
      </div>

      {success && <div className="alert-success">{success}</div>}

      {/* Add Form */}
      {showForm && (
        <div className="card form-card">
          <div className="card-title">Add New Faculty / Staff</div>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="field">
                <label>Employee ID</label>
                <input required placeholder="e.g. KEC001"
                  value={form.employee_id} onChange={set('employee_id')} />
              </div>
              <div className="field">
                <label>Full Name</label>
                <input required placeholder="Faculty Name"
                  value={form.name} onChange={set('name')} />
              </div>
              <div className="field">
                <label>Department</label>
                <select required value={form.department} onChange={set('department')}>
                  <option value="">Select Department</option>
                  {master.departments.map(d => (
                    <option key={d.id} value={d.code}>{d.code} — {d.name}</option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label>Designation</label>
                <select value={form.designation} onChange={set('designation')}>
                  <option value="">Select Designation</option>
                  <option>Professor</option>
                  <option>Associate Professor</option>
                  <option>Assistant Professor</option>
                  <option>Senior Lecturer</option>
                  <option>Lecturer</option>
                  <option>Lab Instructor</option>
                </select>
              </div>
              <div className="field">
                <label>Email</label>
                <input type="email" placeholder="faculty@kec.ac.in"
                  value={form.email} onChange={set('email')} />
              </div>
              <div className="field">
                <label>Phone</label>
                <input placeholder="9XXXXXXXXX"
                  value={form.phone} onChange={set('phone')} />
              </div>
            </div>
            {err && <div className="alert-error">{err}</div>}
            <div className="form-actions">
              <button type="submit" className="btn btn-gold" disabled={saving}>
                {saving ? 'Saving…' : 'Add Faculty'}
              </button>
              <button type="button" className="btn btn-outline"
                onClick={() => { setShowForm(false); setErr(''); setForm(EMPTY) }}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filter Bar */}
      <div className="filter-bar card">
        <div className="filter-row">
          <select value={filterDept} onChange={e => setFilterDept(e.target.value)}>
            <option value="">All Departments</option>
            {master.departments.map(d => (
              <option key={d.id} value={d.code}>{d.code}</option>
            ))}
          </select>
          <input className="search-input" placeholder="Search name / emp id…"
            value={search} onChange={e => setSearch(e.target.value)} />
          {!showForm && (
            <button className="btn btn-gold btn-sm" onClick={() => setShowForm(true)}>
              + Add Faculty
            </button>
          )}
        </div>
        <div className="filter-count">
          Showing <strong>{filtered.length}</strong> of {faculty.length} faculty
        </div>
      </div>

      {/* Department-wise sections */}
      {loading ? (
        <div className="loading-row">Loading…</div>
      ) : (filterDept ? (
        <DeptSection
          dept={filterDept}
          deptName={master.departments.find(d => d.code === filterDept)?.name}
          staff={byDept[filterDept] || []}
          onDelete={handleDelete}
        />
      ) : (
        master.departments.map(d => (
          <DeptSection
            key={d.code}
            dept={d.code}
            deptName={d.name}
            staff={byDept[d.code] || []}
            onDelete={handleDelete}
          />
        ))
      ))}
    </div>
  )
}

function DeptSection({ dept, deptName, staff, onDelete }) {
  const [open, setOpen] = useState(true)

  return (
    <div className="card dept-section">
      <div className="dept-header" onClick={() => setOpen(o => !o)}>
        <div>
          <span className="dept-badge">{dept}</span>
          {deptName && <span className="dept-name">{deptName}</span>}
        </div>
        <div className="dept-meta">
          <span className="badge badge-blue">{staff.length} staff</span>
          <span className="toggle-icon">{open ? '▲' : '▼'}</span>
        </div>
      </div>

      {open && (
        staff.length === 0 ? (
          <div className="empty-row">No faculty in this department</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Employee ID</th>
                <th>Name</th>
                <th>Designation</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {staff.map((f, i) => (
                <tr key={f.id}>
                  <td className="muted">{i + 1}</td>
                  <td className="mono">{f.employee_id}</td>
                  <td><strong>{f.name}</strong></td>
                  <td>
                    <span className="badge badge-gold">
                      {f.designation || '—'}
                    </span>
                  </td>
                  <td className="muted" style={{ fontSize: '0.78rem' }}>{f.email || '—'}</td>
                  <td className="muted" style={{ fontSize: '0.78rem' }}>{f.phone || '—'}</td>
                  <td>
                    <button className="btn btn-red btn-sm"
                      onClick={() => onDelete(f.id, f.name)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )
      )}
    </div>
  )
}
