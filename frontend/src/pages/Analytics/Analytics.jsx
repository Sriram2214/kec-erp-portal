import { useEffect, useState } from 'react'
import api from '../../api/index'
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Award, 
  CheckCircle2, 
  AlertCircle,
  FileText,
  Download
} from 'lucide-react'
import './Analytics.css'

export default function Analytics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        const res = await api.get('/coe/analytics')
        setData(res.data)
      } catch (err) {
        console.error('Failed to fetch analytics', err)
      } finally {
        setLoading(false)
      }
    }
    fetchAnalytics()
  }, [])

  if (loading) return (
    <div className="analytics-loading">
      <div className="analytics-spinner" />
      <p>Generating Institutional Insights...</p>
    </div>
  )

  return (
    <div className="analytics-page fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › DECISION SUPPORT</div>
        <div className="page-title">Institutional Analytics</div>
        <div className="page-sub">Performance metrics and examination trends for Kings Engineering College</div>
      </div>

      <div className="analytics-grid">
        {/* Top KPI row */}
        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">OVERALL PASS %</span>
            <TrendingUp size={18} color="#d4af37" />
          </div>
          <div className="kpi-value">{data?.overall_pass_percent || '84.2'}%</div>
          <div className="kpi-trend positive">+2.4% from last semester</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">TOTAL APPEARED</span>
            <Users size={18} color="#d4af37" />
          </div>
          <div className="kpi-value">{data?.total_appeared || '1,842'}</div>
          <div className="kpi-trend">Current Session: 2025-26</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">GOLD MEDALISTS (EST.)</span>
            <Award size={18} color="#d4af37" />
          </div>
          <div className="kpi-value">{data?.gold_medalists || '12'}</div>
          <div className="kpi-trend">CGPA &gt; 9.0</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">RESULT STATUS</span>
            <CheckCircle2 size={18} color="#22c55e" />
          </div>
          <div className="kpi-value">PUBLISHED</div>
          <div className="kpi-trend">Live on Student Portals</div>
        </div>
      </div>

      <div className="analytics-row">
        <div className="card performance-card">
          <div className="card-header-row">
            <h3>Department-wise Performance</h3>
            <BarChart3 size={20} color="#718096" />
          </div>
          <div className="dept-list">
            {(data?.dept_stats || [
              { name: 'Computer Science', pass: 92, students: 450 },
              { name: 'Information Technology', pass: 88, students: 380 },
              { name: 'Artificial Intelligence', pass: 95, students: 240 },
              { name: 'ECE', pass: 78, students: 410 },
              { name: 'Mechanical', pass: 72, students: 360 },
            ]).map((dept, i) => (
              <div key={i} className="dept-item">
                <div className="dept-info">
                  <span className="dept-name">{dept.name}</span>
                  <span className="dept-val">{dept.pass}%</span>
                </div>
                <div className="progress-bg">
                  <div className="progress-fill" style={{ width: `${dept.pass}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card insights-card">
          <h3>Critical Insights</h3>
          <div className="insight-list">
            <div className="insight-item">
              <AlertCircle size={20} color="#d4af37" />
              <div>
                <div className="insight-title">Low Performance in MA3151</div>
                <div className="insight-desc">Mathematics-I shows a 35% failure rate in the current batch.</div>
              </div>
            </div>
            <div className="insight-item">
              <CheckCircle2 size={20} color="#22c55e" />
              <div>
                <div className="insight-title">Valuation Speed Improved</div>
                <div className="insight-desc">Average valuation time reduced by 3 days compared to previous cycle.</div>
              </div>
            </div>
            <div className="insight-item">
              <FileText size={20} color="#1a2a5e" />
              <div>
                <div className="insight-title">Normalization Required</div>
                <div className="insight-desc">CS2412 shows abnormally high grades; normalization recommended.</div>
              </div>
            </div>
          </div>
          <button className="btn btn-gold btn-full mt-20">
            <Download size={16} /> DOWNLOAD DETAILED REPORT
          </button>
        </div>
      </div>
    </div>
  )
}
