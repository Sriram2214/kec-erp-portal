import { useEffect, useState, useRef } from 'react'
import api from '../../api/index'
import { X, Ticket, CheckCircle, Megaphone, ChevronUp, ChevronDown } from 'lucide-react'
import './Students.css'

const YEARS = [1,2,3,4]
const SEMS  = [1,2,3,4,5,6,7,8]
const EMPTY = {
  register_number:'', name:'', department:'', degree:'',
  batch:'', academic_year:'', semester:'', regulation:'',
  email:'', phone:'', dob:''
}

export default function Students() {
  const [students,   setStudents]   = useState([])
  const [master,     setMaster]     = useState({ departments:[], batches:[], regulations:[], degrees:[] })
  const [loading,    setLoading]    = useState(true)

  // Add mode: 'none' | 'individual' | 'excel'
  const [addMode,    setAddMode]    = useState('none')
  const [form,       setForm]       = useState(EMPTY)
  const [saving,     setSaving]     = useState(false)
  const [err,        setErr]        = useState('')
  const [success,    setSuccess]    = useState('')

  // Excel upload
  const fileRef                         = useRef()
  const [xlFile,     setXlFile]         = useState(null)
  const [uploading,  setUploading]      = useState(false)
  const [uploadResult, setUploadResult] = useState(null)

  // Filters
  const [filterDept,  setFilterDept]  = useState('')
  const [filterBatch, setFilterBatch] = useState('')
  const [filterYear,  setFilterYear]  = useState('')
  const [search,      setSearch]      = useState('')

  const load = () => {
    setLoading(true)
    api.get('/students')
      .then(r => {
        const data = r.data
        setStudents(Array.isArray(data) ? data : (data.students || []))
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
    api.get('/master')
      .then(r => {
        if (r.data && r.data.departments && r.data.departments.length > 0) {
          setMaster(r.data)
        } else {
          throw new Error('Empty master data')
        }
      })
      .catch(() => {
        // Fallback master data if backend fails
        setMaster({
          departments: [
            { id: 1, code: 'AI&DS', name: 'Artificial Intelligence and Data Science' },
            { id: 2, code: 'AIML', name: 'Artificial Intelligence and Machine Learning' },
            { id: 3, code: 'BME', name: 'Biomedical Engineering' },
            { id: 4, code: 'CSE', name: 'Computer Science and Engineering' },
            { id: 5, code: 'ECE', name: 'Electronics and Communication Engineering' },
            { id: 6, code: 'IT', name: 'Information Technology' },
            { id: 7, code: 'MECH', name: 'Mechanical Engineering' },
            { id: 8, code: 'RAA', name: 'Robotics and Automation' }
          ],
          degrees: [
            { id: 1, name: 'B.E' }, { id: 2, name: 'B.TECH' },
            { id: 3, name: 'M.E' }, { id: 4, name: 'PhD.' }
          ],
          batches: [
            { id: 1, label: '2021-2025' }, { id: 2, label: '2022-2026' },
            { id: 3, label: '2023-2027' }, { id: 4, label: '2024-2028' }
          ],
          regulations: [
            { id: 1, name: 'R2021' }, { id: 2, name: 'R2019' }
          ]
        })
      })
  }, [])

  const toggleResult = async (sid) => {
    try {
      await api.post(`/students/${sid}/toggle-result`)
      load()
    } catch (err) {
      alert("Failed to toggle result status")
    }
  }

  const filtered = students.filter(s => {
    if (filterDept  && s.department   !== filterDept)          return false
    if (filterBatch && s.batch        !== filterBatch)         return false
    if (filterYear  && String(s.academic_year) !== filterYear) return false
    if (search && !s.name.toLowerCase().includes(search.toLowerCase()) &&
                  !s.register_number.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const byDept = (master.departments || []).reduce((acc, d) => {
    acc[d.code] = filtered.filter(s => s.department === d.code)
    return acc
  }, {})

  const handleSubmit = async e => {
    e.preventDefault()
    setErr(''); setSaving(true)
    try {
      await api.post('/students', form)
      setSuccess('Student added successfully!')
      setForm(EMPTY); setAddMode('none'); load()
      setTimeout(() => setSuccess(''), 3000)
    } catch(ex) {
      setErr(ex.response?.data?.message || 'Failed to add student')
    } finally { setSaving(false) }
  }

  const handleExcelUpload = async () => {
    if (!xlFile) return
    setErr(''); setUploading(true); setUploadResult(null)
    const fd = new FormData()
    fd.append('file', xlFile)
    try {
      const res = await api.post('/students/bulk', fd)
      setUploadResult(res.data)
      setXlFile(null)
      if (fileRef.current) fileRef.current.value = ''
      load()
    } catch(ex) {
      setErr(ex.response?.data?.message || 'Upload failed')
    } finally { setUploading(false) }
  }

  const downloadTemplate = () => {
    window.open('/api/students/template', '_blank')
  }

  const handleDelete = async (id, name) => {
    if (!confirm(`Delete ${name}?`)) return
    await api.delete(`/students/${id}`); load()
  }

  const set = k => e => setForm(f => ({...f, [k]: e.target.value}))
  const closeForm = () => { setAddMode('none'); setErr(''); setForm(EMPTY); setXlFile(null); setUploadResult(null) }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Students</div>
        <div className="page-title">Students</div>
        <div className="page-sub">Department-wise, Batch-wise Student Records</div>
      </div>

      {success && <div className="alert-success">{success}</div>}

      {/* ── Add Panel ── */}
      {addMode !== 'none' && (
        <div className="card form-card">
          <div className="add-tabs">
            <button
              className={`add-tab ${addMode === 'individual' ? 'active' : ''}`}
              onClick={() => { setAddMode('individual'); setErr(''); setUploadResult(null) }}>
              Individual Add
            </button>
            <button
              className={`add-tab ${addMode === 'excel' ? 'active' : ''}`}
              onClick={() => { setAddMode('excel'); setErr('') }}>
              Excel Upload
            </button>
            <button className="add-tab-close" onClick={closeForm}>
              <X size={16} /> Close
            </button>
          </div>

          {addMode === 'individual' && (
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="field">
                  <label>Degree</label>
                  <select required value={form.degree} onChange={set('degree')}>
                    <option value="">Select Degree</option>
                    {master.degrees?.map(d => <option key={d.id} value={d.name}>{d.name}</option>)}
                  </select>
                </div>
                <div className="field">
                  <label>Department</label>
                  <select required value={form.department} onChange={set('department')}>
                    <option value="">Select Department</option>
                    {master.departments?.map(d => (
                      <option key={d.id} value={d.code}>{d.code} — {d.name}</option>
                    ))}
                  </select>
                </div>
                <div className="field">
                  <label>Batch</label>
                  <select required value={form.batch} onChange={set('batch')}>
                    <option value="">Select Batch</option>
                    {master.batches?.map(b => <option key={b.id} value={b.label}>{b.label}</option>)}
                  </select>
                </div>
                <div className="field">
                  <label>Regulation</label>
                  <select required value={form.regulation} onChange={set('regulation')}>
                    <option value="">Select Regulation</option>
                    {master.regulations?.map(r => <option key={r.id} value={r.name}>{r.name}</option>)}
                  </select>
                </div>
                <div className="field">
                  <label>Register Number</label>
                  <input required placeholder="e.g. 211CS001" value={form.register_number} onChange={set('register_number')} />
                </div>
                <div className="field">
                  <label>Full Name</label>
                  <input required placeholder="Student Name" value={form.name} onChange={set('name')} />
                </div>
                <div className="field">
                  <label>Academic Year</label>
                  <select required value={form.academic_year} onChange={set('academic_year')}>
                    <option value="">Select</option>
                    {YEARS.map(y => <option key={y} value={y}>Year {y}</option>)}
                  </select>
                </div>
                <div className="field">
                  <label>Semester</label>
                  <select required value={form.semester} onChange={set('semester')}>
                    <option value="">Select</option>
                    {SEMS.map(s => <option key={s} value={s}>Semester {s}</option>)}
                  </select>
                </div>
                <div className="field">
                  <label>Email</label>
                  <input type="email" placeholder="student@kec.ac.in" value={form.email} onChange={set('email')} />
                </div>
                <div className="field">
                  <label>Phone</label>
                  <input placeholder="9XXXXXXXXX" value={form.phone} onChange={set('phone')} />
                </div>
                <div className="field">
                  <label>Date of Birth</label>
                  <input type="date" value={form.dob} onChange={set('dob')} />
                </div>
              </div>
              {err && <div className="alert-error">{err}</div>}
              <div className="form-actions">
                <button type="submit" className="btn btn-gold" disabled={saving}>
                  {saving ? 'Saving…' : 'Add Student'}
                </button>
              </div>
            </form>
          )}

          {addMode === 'excel' && (
            <div className="excel-upload-area">
              <div className="excel-info-row">
                <div className="excel-tip">
                  <strong>Step 1:</strong> Download the template → fill student data → upload
                </div>
                <button className="btn btn-outline" onClick={downloadTemplate}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight:'5px',verticalAlign:'middle'}}>
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                  Download Template (.xlsx)
                </button>
              </div>

              <div className="excel-drop-zone"
                onClick={() => fileRef.current?.click()}
                onDragOver={e => e.preventDefault()}
                onDrop={e => {
                  e.preventDefault()
                  const f = e.dataTransfer.files[0]
                  if (f) setXlFile(f)
                }}>
                <div className="excel-icon">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#1d6f42" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" fill="#e8f5e9" stroke="#1d6f42"/>
                    <path d="M3 9h18M3 15h18M9 3v18" stroke="#1d6f42"/>
                    <path d="M7 12l2 2 4-4" stroke="#1d6f42" strokeWidth="1.8"/>
                  </svg>
                </div>
                {xlFile ? (
                  <div>
                    <div className="excel-file-name">{xlFile.name}</div>
                    <div className="excel-file-size">{(xlFile.size/1024).toFixed(1)} KB</div>
                  </div>
                ) : (
                  <div>
                    <div className="excel-drop-text">Click or drag & drop your Excel file here</div>
                    <div className="excel-drop-sub">Supports .xlsx files only</div>
                  </div>
                )}
                <input ref={fileRef} type="file" accept=".xlsx,.xls"
                  style={{ display:'none' }}
                  onChange={e => setXlFile(e.target.files[0])} />
              </div>

              {err && <div className="alert-error">{err}</div>}

              {uploadResult && (
                <div className={`upload-result ${uploadResult.added > 0 ? 'success' : 'warn'}`}>
                  <strong>{uploadResult.message}</strong>
                  {uploadResult.errors?.length > 0 && (
                    <ul className="upload-errors">
                      {uploadResult.errors.map((e,i) => <li key={i}>{e}</li>)}
                    </ul>
                  )}
                </div>
              )}

              <div className="form-actions" style={{ marginTop: '1rem' }}>
                <button className="btn btn-gold" onClick={handleExcelUpload}
                  disabled={!xlFile || uploading}>
                  {uploading ? 'Uploading…' : 'Upload & Add Students'}
                </button>
                {xlFile && (
                  <button className="btn btn-outline"
                    onClick={() => { setXlFile(null); if(fileRef.current) fileRef.current.value=''; setUploadResult(null) }}>
                    Clear
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── Filter Bar ── */}
      <div className="filter-bar card">
        <div className="filter-row">
          <div className="filter-group">
            <select value={filterDept} onChange={e => setFilterDept(e.target.value)}>
              <option value="">All Departments</option>
              {master.departments.map(d => <option key={d.id} value={d.code}>{d.code}</option>)}
            </select>
            <select value={filterBatch} onChange={e => setFilterBatch(e.target.value)}>
              <option value="">All Batches</option>
              {master.batches.map(b => <option key={b.id} value={b.label}>{b.label}</option>)}
            </select>
            <select value={filterYear} onChange={e => setFilterYear(e.target.value)}>
              <option value="">All Years</option>
              {YEARS.map(y => <option key={y} value={y}>Year {y}</option>)}
            </select>
          </div>
          
          <div className="search-wrap">
            <input className="search-input" placeholder="Search name or register number…"
              value={search} onChange={e => setSearch(e.target.value)} />
          </div>

          {addMode === 'none' && (
            <div className="action-buttons">
              <button className="btn btn-gold btn-sm" onClick={() => setAddMode('individual')}>
                <span className="btn-icon">+</span> Add Individual
              </button>
              <button className="btn btn-outline btn-sm" onClick={() => setAddMode('excel')}>
                Upload Excel
              </button>
            </div>
          )}
        </div>
        <div className="filter-footer">
          <div className="filter-count">
            Found <strong>{filtered.length}</strong> matching records <span>(Total: {students.length})</span>
          </div>
        </div>
      </div>

      {/* ── Sections ── */}
      {loading ? (
        <div className="loading-row">Loading…</div>
      ) : (filterDept ? (
        <DeptSection dept={filterDept} students={byDept[filterDept] || []} onDelete={handleDelete} onToggleResult={toggleResult} />
      ) : (
        master.departments.map(d => (
          <DeptSection key={d.code} dept={d.code} deptName={d.name}
            students={byDept[d.code] || []} onDelete={handleDelete} onToggleResult={toggleResult} />
        ))
      ))}
    </div>
  )
}

function DeptSection({ dept, deptName, students, onDelete, onToggleResult }) {
  const [open, setOpen] = useState(true)
  return (
    <div className="card dept-section">
      <div className="dept-header" onClick={() => setOpen(o => !o)}>
        <div>
          <span className="dept-badge">{dept}</span>
          {deptName && <span className="dept-name">{deptName}</span>}
        </div>
        <div className="dept-meta">
          <span className="badge badge-blue">{students.length} students</span>
          <span className="toggle-icon">{open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}</span>
        </div>
      </div>

      {open && (
        students.length === 0 ? (
          <div className="empty-row">No students in this department</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Reg. Number</th>
                <th>Name</th>
                <th>Batch</th>
                <th>Year / Sem</th>
                <th>Regulation</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s, idx) => (
                <tr key={s.id}>
                  <td className="muted">{idx + 1}</td>
                  <td className="mono">{s.register_number}</td>
                  <td><strong>{s.name}</strong></td>
                  <td>{s.batch}</td>
                  <td><span className="badge badge-gold">Y{s.academic_year} / S{s.semester || '-'}</span></td>
                  <td><span className="badge badge-blue">{s.regulation || 'R2021'}</span></td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.4rem' }}>
                      <button 
                        className="btn btn-outline btn-sm"
                        onClick={() => window.open(`/api/ese/hallticket-pdf?regno=${s.register_number}`, '_blank')}
                        title="Download Hall Ticket"
                      >
                        <Ticket size={14} /> Hall Ticket
                      </button>
                      
                      <button 
                        className={`btn btn-sm ${s.result_published ? 'btn-green' : 'btn-outline'}`}
                        onClick={() => onToggleResult(s.id)}
                      >
                        {s.result_published ? <><CheckCircle size={14} /> Published</> : <><Megaphone size={14} /> Release</>}
                      </button>

                      <button className="btn btn-red btn-sm"
                        onClick={() => onDelete(s.id, s.name)}>Delete</button>
                    </div>
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
