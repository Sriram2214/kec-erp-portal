import { useEffect, useState } from 'react'
import api from '../../api/index'
import '../Students/Students.css'

export default function Clearance() {
  const [students, setStudents] = useState([])
  const [loading,  setLoading]  = useState(true)
  const [ay,       setAY]       = useState(null)
  const [saving,   setSaving]   = useState(null) // ID of student being saved
  const [search,   setSearch]   = useState('')

  const loadData = async (ayId) => {
    setLoading(true)
    try {
      const res = await api.get(`/exam/clearance?ay_id=${ayId}`)
      setStudents(res.data)
    } catch {}
    finally { setLoading(false) }
  }

  useEffect(() => {
    api.get('/master').then(r => {
      const curr = r.data.academic_years.find(a => a.is_current)
      setAY(curr)
      if (curr) loadData(curr.id)
    })
  }, [])

  const toggle = async (sid, key, val) => {
    setSaving(sid)
    try {
      await api.post('/exam/clearance', {
        student_id: sid,
        academic_year_id: ay.id,
        [key]: val
      })
      // Local update for speed
      setStudents(prev => prev.map(s => s.id === sid ? { ...s, [key]: val } : s))
    } catch {}
    finally { setSaving(null) }
  }

  const filtered = students.filter(s => 
    s.name.toLowerCase().includes(search.toLowerCase()) ||
    s.regno.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Exam Workflow</div>
        <div className="page-title">Fee & Attendance Clearance</div>
        <div className="page-sub">Approval for Hall Ticket Generation (Item 16)</div>
      </div>

      <div className="filter-bar card">
        <div className="filter-row">
          <input 
            className="search-input" 
            placeholder="Search student by name or regno..." 
            value={search} 
            onChange={e => setSearch(e.target.value)} 
          />
          <div className="ay-badge">Current AY: {ay?.label}</div>
        </div>
      </div>

      <div className="card">
        {loading ? <div className="loading-row">Loading clearance records...</div> : (
          <table className="ese-table">
            <thead>
              <tr>
                <th>Reg. Number</th>
                <th>Name</th>
                <th style={{ textAlign: 'center' }}>Exam Fee</th>
                <th style={{ textAlign: 'center' }}>College Fee</th>
                <th style={{ textAlign: 'center' }}>Attendance</th>
                <th style={{ textAlign: 'center' }}>Hall Ticket Approval</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(s => (
                <tr key={s.id}>
                  <td className="mono">{s.regno}</td>
                  <td><strong>{s.name}</strong> <span className="muted">({s.dept})</span></td>
                  <td align="center">
                    <input type="checkbox" checked={s.exam_fee} onChange={e => toggle(s.id, 'exam_fee_paid', e.target.checked)} />
                  </td>
                  <td align="center">
                    <input type="checkbox" checked={s.college_fee} onChange={e => toggle(s.id, 'college_fee_paid', e.target.checked)} />
                  </td>
                  <td align="center">
                    <input type="checkbox" checked={s.attendance} onChange={e => toggle(s.id, 'attendance_ok', e.target.checked)} />
                  </td>
                  <td align="center">
                    <button 
                      className={`btn btn-sm ${s.approved ? 'btn-green' : 'btn-outline'}`}
                      onClick={() => toggle(s.id, 'approved', !s.approved)}
                      disabled={saving === s.id}
                    >
                      {saving === s.id ? '...' : s.approved ? 'Approved ✓' : 'Approve'}
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
