import { useEffect, useState } from 'react'
import api from '../../api/index'
import { ShieldCheck, Lock, FileText, Zap } from 'lucide-react'
import './Security.css'

export default function Security() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchSecurity = () => {
    setLoading(true)
    api.get('/dashboard/security-status')
      .then(r => setStatus(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchSecurity()
    const timer = setInterval(fetchSecurity, 10000) // Auto-refresh every 10s
    return () => clearInterval(timer)
  }, [])

  if (loading && !status) return <div className="loading-row">Loading Security Data…</div>

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Security & Audit</div>
        <div className="page-title">Security Center</div>
        <div className="page-sub">System Integrity & User Activity Monitor</div>
      </div>

      <div className="security-grid">
        {/* System Health Cards */}
        <div className="status-card">
          <div className="status-header">
            <div className="status-icon success"><ShieldCheck size={20} /></div>
            <div>
              <div className="status-label">Database Status</div>
              <div className="status-value">{status?.database}</div>
            </div>
          </div>
        </div>

        <div className="status-card">
          <div className="status-header">
            <div className="status-icon success"><Lock size={20} /></div>
            <div>
              <div className="status-label">CSRF Protection</div>
              <div className="status-value">{status?.csrf_protection}</div>
            </div>
          </div>
        </div>

        <div className="status-card">
          <div className="status-header">
            <div className="status-icon success"><FileText size={20} /></div>,StartLine:57,TargetContent:
            <div>
              <div className="status-label">Security Headers</div>
              <div className="status-value">{status?.security_headers}</div>
            </div>
          </div>
        </div>

        <div className="status-card">
          <div className="status-header">
            <div className="status-icon success"><Zap size={20} /></div>
            <div>
              <div className="status-label">Rate Limiting</div>
              <div className="status-value">{status?.rate_limiting}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="card audit-log-card">
        <div className="card-title">Recent Activity (Audit Log)</div>
        <div className="audit-table-container">
          <table className="audit-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>User</th>
                <th>Action</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {status?.logs?.length > 0 ? (
                status.logs.map((log, i) => (
                  <tr key={i}>
                    <td className="mono" style={{ fontSize: '0.8rem' }}>
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td>
                      <div className="log-user">
                        <span className="user-initial">{log.user[0].toUpperCase()}</span>
                        <div>
                          <strong>{log.user}</strong>
                          <div className="muted" style={{ fontSize: '0.7rem' }}>{log.role}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${getActionColor(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="details-cell">
                      <pre>{JSON.stringify(log.details, null, 2)}</pre>
                    </td>
                  </tr>
                ))
              ) : (
                <tr><td colSpan="4" className="empty-row">No activity recorded yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function getActionColor(action) {
  if (action.includes('LOGIN')) return 'badge-blue'
  if (action.includes('DELETE')) return 'badge-red'
  if (action.includes('PUBLISH') || action.includes('RELEASE')) return 'badge-gold'
  return 'badge-blue'
}
