import { useEffect, useState } from 'react'
import api from '../../api/index'
import './Registration.css'

export default function Registration() {
  const [courses,   setCourses]   = useState([])
  const [selected,  setSelected]  = useState([])
  const [ay,        setAY]        = useState(null)
  const [loading,   setLoading]   = useState(true)
  const [saving,    setSaving]    = useState(false)
  const [registered, setRegistered] = useState([])
  const [msg,       setMsg]       = useState('')

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const [cRes, mRes, rRes] = await Promise.all([
          api.get('/courses'),
          api.get('/master'),
          api.get('/exam/my-registrations')
        ])
        setCourses(cRes.data)
        const currAY = mRes.data.academic_years.find(a => a.is_current)
        setAY(currAY)
        setRegistered(rRes.data)
      } catch {}
      finally { setLoading(false) }
    }
    load()
  }, [])

  const toggleCourse = (id) => {
    if (selected.includes(id)) setSelected(selected.filter(i => i !== id))
    else setSelected([...selected, id])
  }

  const handleSubmit = async () => {
    if (selected.length === 0) return alert('Select at least one course')
    setSaving(true)
    try {
      await api.post('/exam/register', {
        course_ids: selected,
        academic_year_id: ay?.id
      })
      setMsg('Registration Successful! ✓')
      window.scrollTo(0,0)
    } catch {
      setMsg('Error in registration.')
    } finally { setSaving(false) }
  }

  if (loading) return <div className="loading-row">Loading exam registration...</div>

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Exam Workflow</div>
        <div className="page-title">Course Registration</div>
        <div className="page-sub">Current Semester Exam Registration (Item 15)</div>
      </div>

      {msg && <div className="alert-success">{msg}</div>}

      <div className="reg-container">
        <div className="card reg-info">
          <div className="card-title">Registration Status</div>
          <div className="reg-ay">
            Current Academic Year: <strong>{ay?.label || 'N/A'} ({ay?.semester})</strong>
          </div>
          <div className="reg-stat-grid">
            <div className="reg-stat-item">
              <span className="label">Registered Courses</span>
              <span className="value">{registered.length}</span>
            </div>
          </div>
        </div>

        <div className="card reg-table-card">
          <div className="card-title">Select Courses for Registration</div>
          <table className="ese-table">
            <thead>
              <tr>
                <th style={{ width: '10%' }}>Select</th>
                <th style={{ width: '20%' }}>Code</th>
                <th>Course Title</th>
                <th style={{ width: '15%' }}>Credits</th>
              </tr>
            </thead>
            <tbody>
              {courses.map(c => (
                <tr key={c.id} className={selected.includes(c.id) ? 'selected-row' : ''}>
                  <td align="center">
                    <input 
                      type="checkbox" 
                      checked={selected.includes(c.id)} 
                      onChange={() => toggleCourse(c.id)} 
                    />
                  </td>
                  <td className="mono">{c.course_code}</td>
                  <td><strong>{c.course_title}</strong></td>
                  <td>{c.credits}</td>
                </tr>
              ))}
            </tbody>
          </table>
          
          <div className="reg-actions">
            <button 
              className="btn btn-gold w-100" 
              onClick={handleSubmit} 
              disabled={saving || selected.length === 0}
            >
              {saving ? 'Processing...' : 'Confirm Registration'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
