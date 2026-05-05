import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../api/index'
import './COE.css'

export default function COEModule() {
  const navigate = useNavigate()
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [session, setSession] = useState('FN')
  const [data, setData] = useState([])
  const [dispatchData, setDispatchData] = useState(null)
  const [revals, setRevals] = useState([])
  const [loading, setLoading] = useState(false)
  const [dummyBatch, setDummyBatch] = useState('2021-2025')
  const [dummySem, setDummySem] = useState(6)
  const [msg, setMsg] = useState('')

  const generateDummies = async () => {
    try {
      const res = await api.post('/coe/generate-dummies', { batch: dummyBatch, semester: dummySem })
      setMsg(res.data.message)
      setTimeout(() => setMsg(''), 5000)
    } catch { alert('Failed to generate dummy numbers.') }
  }

  const loadSessionReport = async () => {
    setLoading(true)
    try {
      const res = await api.get(`/coe/session-report?date=${date}&session=${session}`)
      setData(res.data)
      const dRes = await api.get(`/coe/dispatch-report?date=${date}`)
      setDispatchData(dRes.data)
      const rRes = await api.get('/coe/revaluation-list')
      setRevals(rRes.data)
    } catch {}
    finally { setLoading(false) }
  }

  useEffect(() => { loadSessionReport() }, [date, session])

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KCE ERP › COE Module</div>
        <div className="page-title">COE Command Center</div>
        <div className="page-sub">Operational headquarters for exam-day management and specialized institutional reports.</div>
      </div>

      <div className="filter-bar card">
        <div className="filter-row">
          <div className="field">
            <label>Exam Date</label>
            <input type="date" value={date} onChange={e => setDate(e.target.value)} />
          </div>
          <div className="field">
            <label>Session</label>
            <select value={session} onChange={e => setSession(e.target.value)}>
              <option>FN</option>
              <option>AN</option>
            </select>
          </div>
        </div>
      </div>

      <div className="coe-grid">
        {/* Session Summary (Item 21) */}
        <div className="card">
          <div className="card-title">Session-wise Strength Report</div>
          {loading ? <div className="loading-row">Loading...</div> : (
            <table className="ese-table">
              <thead>
                <tr><th>Course</th><th>Dept</th><th>Strength</th><th>Action</th></tr>
              </thead>
              <tbody>
                {(data || []).map((item, i) => (
                  <tr key={i}>
                    <td className="mono clickable" onClick={() => navigate(`/ese-attendance?course_code=${item.course_code}`)}>
                      <strong>{item.course_code}</strong>
                    </td>
                    <td>{item.dept}</td>
                    <td>{item.student_count}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button className="btn btn-sm btn-outline" onClick={() => navigate(`/ese-attendance?course_code=${item.course_code}`)}>
                          Attendance
                        </button>
                        <button className="btn btn-sm btn-gold">QP Cover</button>
                      </div>
                    </td>
                  </tr>
                ))}
                {data.length === 0 && <tr><td colSpan="4" className="empty-row">No exams scheduled for this session.</td></tr>}
              </tbody>
            </table>
          )}
        </div>

        {/* Quick Tools */}
        <div className="card coe-tools">
          <div className="card-title">COE Quick Tools</div>
          <div className="tools-list">
            <div className="tool-item">
              <div className="tool-info">
                <strong>QP Cover Generation</strong>
                <p>Generate covers for current session</p>
              </div>
              <button className="btn btn-sm btn-gold">Download All</button>
            </div>
            <div className="tool-item">
              <div className="tool-info">
                <strong>Attendance Monitoring</strong>
                <p>Check missing attendance entries</p>
              </div>
              <button className="btn btn-sm btn-outline">View Alerts</button>
            </div>
            <div className="tool-item">
              <div className="tool-info">
                <strong>Dispatch Management</strong>
                <p>Generate final dispatch bundles</p>
              </div>
              <button className="btn btn-sm btn-outline">Generate</button>
            </div>
          </div>
        </div>
      </div>

      <div className="card coe-card" style={{ marginTop: '2rem' }}>
        <div className="card-title">Confidential Dummy Number Engine</div>
        <p className="muted">Generate semester-wide confidential IDs to replace Register Numbers during valuation.</p>
        
        <div className="filter-row" style={{ marginTop: '1.5rem', gap: '2rem' }}>
          <div className="field">
            <label>Target Batch</label>
            <input type="text" value={dummyBatch} onChange={e => setDummyBatch(e.target.value)} />
          </div>
          <div className="field">
            <label>Semester</label>
            <input type="number" value={dummySem} onChange={e => setDummySem(e.target.value)} />
          </div>
          <button className="btn btn-gold" style={{ marginTop: '20px' }} onClick={generateDummies}>
            Generate Dummy Mapping
          </button>
        </div>

        {msg && <div className="status-msg success" style={{ marginTop: '1rem', color: 'var(--gold-vivid)', fontWeight: 'bold' }}>{msg}</div>}
      </div>

      {dispatchData && (
        <div className="card fade-in" style={{ marginTop: '2rem' }}>
          <div className="ese-toolbar">
            <div className="card-title">Master Dispatch Summary (University Copy)</div>
            <button className="btn btn-sm btn-gold" onClick={() => window.print()}>Print Dispatch List</button>
          </div>
          <table className="ese-table">
            <thead>
              <tr><th>Course</th><th>Title</th><th>Total scripts</th><th>Bundles (25s)</th><th>Session</th></tr>
            </thead>
            <tbody>
              {(dispatchData?.items || []).map((item, i) => (
                <tr key={i}>
                  <td className="mono"><strong>{item.course_code}</strong></td>
                  <td>{item.title}</td>
                  <td>{item.strength}</td>
                  <td><span className="badge badge-gold">{item.bundles} Bundles</span></td>
                  <td>{item.session}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {revals.length > 0 && (
        <div className="card fade-in" style={{ marginTop: '2rem' }}>
          <div className="card-title">Revaluation Command Center</div>
          <table className="ese-table">
            <thead>
              <tr><th>Dummy No.</th><th>Old Mark</th><th>New Mark</th><th>Status</th><th>Action</th></tr>
            </thead>
            <tbody>
              {(revals || []).map(r => (
                <tr key={r.id}>
                  <td className="mono">{r.dummy_no}</td>
                  <td>{r.old_mark}</td>
                  <td>
                    <input type="number" className="mono-input" style={{ width: '80px' }} placeholder="Mark" />
                  </td>
                  <td><span className="badge badge-blue">Pending Review</span></td>
                  <td>
                    <button className="btn btn-sm btn-gold">Update</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
