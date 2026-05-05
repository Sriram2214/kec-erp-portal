import { useEffect, useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import api from '../../api/index'
import { Search, Printer, RefreshCw, FileText, User } from 'lucide-react'
import './Results.css'

export default function Results() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searchRegNo, setSearchRegNo] = useState('')

  const isAdmin = user?.role === 'admin' || user?.role === 'coe'

  async function fetchResults(regno = '') {
    setLoading(true)
    setError('')
    try {
      const url = isAdmin ? `/results/my?regno=${regno}` : '/results/my'
      const res = await api.get(url)
      setData(res.data)
    } catch (e) {
      setError(e.response?.data?.message || 'Failed to fetch results.')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!isAdmin) {
      fetchResults()
    }
  }, [isAdmin])

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchRegNo) fetchResults(searchRegNo)
  }

  if (loading && !isAdmin) return (
    <div className="res-loading">
      <div className="res-spinner" />
      <p>Fetching institutional records...</p>
    </div>
  )

  return (
    <div className="res-page fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › EXAM CONTROL</div>
        <div className="page-title">{isAdmin ? 'Result Master' : 'My Examination Results'}</div>
      </div>

      {isAdmin && (
        <div className="card search-card no-print">
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-input-wrap">
              <Search size={18} className="search-icon" />
              <input 
                type="text" 
                placeholder="Enter Student Register Number (e.g. 911221104001)"
                value={searchRegNo}
                onChange={e => setSearchRegNo(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn btn-gold" disabled={loading}>
              {loading ? 'Searching...' : 'Search Record'}
            </button>
          </form>
        </div>
      )}

      {error && (
        <div className="res-error-card card no-print">
          <p>⚠ {error}</p>
          {!isAdmin && <button className="btn btn-gold" onClick={() => fetchResults()}>Try Again</button>}
        </div>
      )}

      {data && (
        <div className="res-container">
          <div className="res-controls no-print">
            <button className="btn btn-sm btn-outline" onClick={() => window.print()}>
              <Printer size={16} /> Print Sheet
            </button>
            <button className="btn btn-sm btn-outline" onClick={() => fetchResults(searchRegNo)}>
              <RefreshCw size={16} /> Refresh
            </button>
          </div>

          <div className="res-sheet" id="printable-result">
            <div className="res-title">{data.session_title}</div>

            <div className="res-student-info">
              <div className="info-box">
                <span className="info-label">REGISTER NUMBER</span>
                <span className="info-val">{data.register_no}</span>
              </div>
              <div className="info-box">
                <span className="info-label">STUDENT NAME</span>
                <span className="info-val">{data.student_name}</span>
              </div>
            </div>

            <table className="res-main-table">
              <thead>
                <tr>
                  <th>SEM</th>
                  <th>COURSE CODE</th>
                  <th>COURSE TITLE</th>
                  <th>GRADE</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((r, i) => (
                  <tr key={i}>
                    <td className="txt-center">{r.semester}</td>
                    <td className="txt-center">{r.course_code}</td>
                    <td>{r.course_title}</td>
                    <td className="txt-center grade-cell">{r.grade}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="res-footer">
              <div className="footer-legend">
                * U - Reappear | AB - Absent | W - Withdrawal | WH1 - Withheld
              </div>
              <div className="footer-audit">
                Computer Generated Statement. Printed on {new Date().toLocaleDateString()}
              </div>
            </div>
          </div>
        </div>
      )}

      {isAdmin && !data && !error && (
        <div className="res-placeholder card">
          <FileText size={48} color="#d1d5db" />
          <h3>No Record Loaded</h3>
          <p>Enter a student register number above to view their academic performance sheet.</p>
        </div>
      )}
    </div>
  )
}
