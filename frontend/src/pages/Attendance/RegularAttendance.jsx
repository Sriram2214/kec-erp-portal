import { useEffect, useState } from 'react'
import api from '../../api/index'
import './Attendance.css'

export default function RegularAttendance() {
  const [myAllocs, setMyAllocs] = useState([])
  const [selAlloc,  setSelAlloc]  = useState('')
  const [students,  setStudents]  = useState([])
  const [loading,   setLoading]   = useState(false)
  const [date,      setDate]      = useState(new Date().toISOString().split('T')[0])
  const [period,    setPeriod]    = useState(1)
  const [saving,    setSaving]    = useState(false)
  const [msg,       setMsg]       = useState('')

  useEffect(() => {
    // In a real app, this would be /faculty/my-courses
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
        setStudents(r.data.map(s => ({ ...s, status: 'Present' })))
      })
      .finally(() => setLoading(false))
  }, [selAlloc])

  const handleSave = async () => {
    setSaving(true); setMsg('')
    try {
      await api.post('/faculty/submit-attendance', {
        allocation_id: selAlloc,
        date,
        period,
        students: students.reduce((acc, s) => ({...acc, [s.id]: s.status}), {})
      })
      setMsg('Attendance saved successfully! ✓')
      setTimeout(() => setMsg(''), 3000)
    } catch {
      setMsg('Error saving attendance.')
    } finally { setSaving(false) }
  }

  const toggleStatus = (id) => {
    setStudents(prev => prev.map(s => 
      s.id === id ? { ...s, status: s.status === 'Present' ? 'Absent' : 'Present' } : s
    ))
  }

  const pCount = students.filter(s => s.status === 'Present').length
  const aCount = students.filter(s => s.status === 'Absent').length

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Regular Attendance</div>
        <div className="page-title">Daily Attendance Entry</div>
        <div className="page-sub">Period-wise student attendance for assigned classes (Item 11)</div>
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
            <label>Date</label>
            <input type="date" value={date} onChange={e => setDate(e.target.value)} />
          </div>
          <div className="field">
            <label>Period</label>
            <select value={period} onChange={e => setPeriod(e.target.value)}>
              {[1,2,3,4,5,6,7,8].map(p => <option key={p} value={p}>Period {p}</option>)}
            </select>
          </div>
        </div>
      </div>

      {loading ? <div className="loading-row">Fetching Students...</div> : (
        <>
          <div className="ese-toolbar" style={{ margin: '1rem 0' }}>
            <div className="ese-counts">
              <span className="ese-count present">Present: <strong>{pCount}</strong></span>
              <span className="ese-count absent">Absent: <strong>{aCount}</strong></span>
            </div>
            <button className="btn btn-gold" onClick={handleSave} disabled={saving}>
              {saving ? 'Saving...' : 'Save Attendance'}
            </button>
          </div>

          {msg && <div className={msg.includes('Error') ? 'alert-error' : 'alert-success'}>{msg}</div>}

          <div className="card">
            <table className="ese-table">
              <thead>
                <tr>
                  <th style={{ width: '10%' }}>S.No</th>
                  <th style={{ width: '30%' }}>Reg. Number</th>
                  <th style={{ width: '40%' }}>Student Name</th>
                  <th style={{ width: '20%', textAlign: 'center' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s, i) => (
                  <tr key={s.id} className={s.status === 'Absent' ? 'ese-row-absent' : ''}>
                    <td className="muted">{i + 1}</td>
                    <td className="mono">{s.regno}</td>
                    <td><strong>{s.name}</strong></td>
                    <td align="center">
                      <button 
                        className={`ese-st-btn ${s.status === 'Present' ? 'p active' : 'a active'}`}
                        onClick={() => toggleStatus(s.id)}
                      >
                        {s.status === 'Present' ? 'P' : 'AB'}
                      </button>
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
