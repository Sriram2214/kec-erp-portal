import { useEffect, useState } from 'react'
import api from '../../api/index'
import '../Students/Students.css'

export default function RegularMarks() {
  const [myAllocs, setMyAllocs] = useState([])
  const [selAlloc,  setSelAlloc]  = useState('')
  const [students,  setStudents]  = useState([])
  const [loading,   setLoading]   = useState(false)
  const [assessment, setAssessment] = useState('Internal 1')
  const [saving,    setSaving]    = useState(false)
  const [msg,       setMsg]       = useState('')

  useEffect(() => {
    api.get('/allocations').then(r => {
      setMyAllocs(r.data)
      if (r.data.length > 0) setSelAlloc(r.data[0].id)
    })
  }, [])

  useEffect(() => {
    if (!selAlloc) return
    setLoading(true)
    api.get(`/faculty/students-by-allocation/${selAlloc}`)
      .then(r => {
        setStudents(r.data.map(s => ({ ...s, marks: '', assignment: '' })))
      })
      .finally(() => setLoading(false))
  }, [selAlloc])

  const handleSave = async () => {
    setSaving(true); setMsg('')
    try {
      await api.post('/faculty/submit-marks', {
        allocation_id: selAlloc,
        assessment_name: assessment,
        marks: students.reduce((acc, s) => ({
          ...acc, [s.id]: { marks: s.marks, assignment: s.assignment }
        }), {})
      })
      setMsg('Marks saved successfully! ✓')
      setTimeout(() => setMsg(''), 3000)
    } catch {
      setMsg('Error saving marks.')
    } finally { setSaving(false) }
  }

  const updateVal = (id, key, val) => {
    setStudents(prev => prev.map(s => s.id === id ? { ...s, [key]: val } : s))
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Internal Marks</div>
        <div className="page-title">Internal Assessment Marks</div>
        <div className="page-sub">Entry for Assessment & Assignment Marks (Item 12)</div>
      </div>

      <div className="filter-bar card">
        <div className="filter-row">
          <div className="field">
            <label>Class / Allocation</label>
            <select value={selAlloc} onChange={e => setSelAlloc(e.target.value)}>
              {myAllocs.map(a => (
                <option key={a.id} value={a.id}>
                  {a.course_code} — {a.batch} ({a.section})
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Assessment Type</label>
            <select value={assessment} onChange={e => setAssessment(e.target.value)}>
              <option>Internal 1</option>
              <option>Internal 2</option>
              <option>Internal 3</option>
              <option>Assignment</option>
              <option>Model Exam</option>
            </select>
          </div>
        </div>
      </div>

      {loading ? <div className="loading-row">Fetching Students...</div> : (
        <>
          <div className="ese-toolbar" style={{ margin: '1rem 0' }}>
            <div className="ese-counts">
              <span className="ese-count total">Students: <strong>{students.length}</strong></span>
            </div>
            <button className="btn btn-gold" onClick={handleSave} disabled={saving}>
              {saving ? 'Saving...' : 'Save Marks'}
            </button>
          </div>

          {msg && <div className={msg.includes('Error') ? 'alert-error' : 'alert-success'}>{msg}</div>}

          <div className="card">
            <table className="ese-table">
              <thead>
                <tr>
                  <th style={{ width: '10%' }}>S.No</th>
                  <th style={{ width: '25%' }}>Reg. Number</th>
                  <th style={{ width: '35%' }}>Student Name</th>
                  <th style={{ width: '15%' }}>Assessment (50)</th>
                  <th style={{ width: '15%' }}>Assignment (10)</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s, i) => (
                  <tr key={s.id}>
                    <td className="muted">{i + 1}</td>
                    <td className="mono">{s.regno}</td>
                    <td><strong>{s.name}</strong></td>
                    <td>
                      <input 
                        type="number" className="mono-input" 
                        value={s.marks} onChange={e => updateVal(s.id, 'marks', e.target.value)}
                      />
                    </td>
                    <td>
                      <input 
                        type="number" className="mono-input" 
                        value={s.assignment} onChange={e => updateVal(s.id, 'assignment', e.target.value)}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
