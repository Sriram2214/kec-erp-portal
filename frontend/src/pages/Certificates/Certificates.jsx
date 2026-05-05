import { useEffect, useState } from 'react'
import api from '../../api/index'
import './Certificates.css'

export default function Certificates() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState('')

  useEffect(() => {
    // Mock fetching user data
    setUser({ role: 'student', regno: 'R2021CSE001' })
  }, [])

  const download = async (type) => {
    setLoading(true)
    try {
      const res = await api.get(`/certificates/${type}`)
      setMsg(res.data.message)
      setTimeout(() => setMsg(''), 5000)
    } catch {
      setMsg('Download failed. Contact office.')
    } finally { setLoading(false) }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Certificates</div>
        <div className="page-title">Digital Certificates</div>
        <div className="page-sub">Official Grade Sheets & Provisional Certificates (Items 33-35)</div>
      </div>

      {msg && <div className="alert-success">{msg}</div>}

      <div className="cert-grid">
        <div className="card cert-card">
          <div className="cert-icon">📜</div>
          <div className="cert-info">
            <h3>Semester Grade Sheet</h3>
            <p>Download your official mark sheet for the current semester.</p>
            <button className="btn btn-gold w-100" onClick={() => download('grade-sheet')} disabled={loading}>
              Download Grade Sheet (PDF)
            </button>
          </div>
        </div>

        <div className="card cert-card">
          <div className="cert-icon">📑</div>
          <div className="cert-info">
            <h3>Consolidated Mark Sheet</h3>
            <p>Full history of all marks from Semester 1 to current.</p>
            <button className="btn btn-gold w-100" onClick={() => download('consolidated')} disabled={loading}>
              Download Consolidated
            </button>
          </div>
        </div>

        <div className="card cert-card">
          <div className="cert-icon">🎓</div>
          <div className="cert-info">
            <h3>Provisional Certificate</h3>
            <p>Available only for final year students with no backlogs.</p>
            <button className="btn btn-outline w-100" onClick={() => download('provisional')} disabled={loading}>
              Download Provisional
            </button>
          </div>
        </div>


        <div className="card cert-card">
          <div className="cert-icon">🔄</div>
          <div className="cert-info">
            <h3>Revaluation Portal</h3>
            <p>Apply for re-totaling or re-valuation of your marks.</p>
            <button className="btn btn-outline w-100">Apply for Reval</button>
          </div>
        </div>
      </div>
    </div>
  )
}
