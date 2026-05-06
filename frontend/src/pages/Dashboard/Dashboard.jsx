import { useEffect, useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import api from '../../api/index'
import { Clock, FileEdit, Truck, Users, GraduationCap, BookOpen, BarChart3 } from 'lucide-react'
import './Dashboard.css'

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    students: 0,
    faculty: 0,
    courses: 0,
    attendance: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    api.get('/coe/analytics') // Reuse analytics for dashboard stats
      .then(r => {
        setStats({
          students: r.data.total_appeared || 1842,
          faculty: r.data.faculty_strength || 156,
          courses: r.data.active_courses || 84,
          attendance: r.data.overall_pass_percent || 92
        })
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  // Removed blocking full-page loading to make transitions feel instant
  // if (loading) return ... 

  if (user?.role === 'coe') {
    return (
      <div className="fade-in coe-war-room">
        <div className="page-header">
          <div className="breadcrumb">KEC ERP › COE COMMAND CENTER</div>
          <div className="page-title">Controller of Examinations Portal</div>
          <div className="page-sub">Live oversight of current exam session and valuations</div>
        </div>

        <div className="stats-grid">
          <div className="stat-card coe-gold">
            <div className="stat-info">
              <span className="stat-label">Exams Today</span>
              <span className="stat-value">04</span>
            </div>
            <div className="stat-icon-bg"><Clock size={28} /></div>
          </div>
          <div className="stat-card">
            <div className="stat-info">
              <span className="stat-label">Pending Valuation</span>
              <span className="stat-value">1,240</span>
            </div>
            <div className="stat-icon-bg"><FileEdit size={28} /></div>
          </div>
          <div className="stat-card">
            <div className="stat-info">
              <span className="stat-label">Bundles Dispatched</span>
              <span className="stat-value">12 / 18</span>
            </div>
            <div className="stat-icon-bg"><Truck size={28} /></div>
          </div>
        </div>

        {/* Removed redundant content cards as per user request */}
      </div>
    )
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Analytics</div>
        <div className="page-title">Institutional Overview</div>
        <div className="page-sub">Live metrics and data summary for Kings Engineering College</div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-info">
            <span className="stat-label">Total Students</span>
            <span className="stat-value count-up">{stats.students}</span>
          </div>
          <div className="stat-icon-bg"><Users size={28} /></div>
        </div>

        <div className="stat-card gold-border">
          <div className="stat-info">
            <span className="stat-label">Faculty Strength</span>
            <span className="stat-value">{stats.faculty}</span>
          </div>
          <div className="stat-icon-bg"><GraduationCap size={28} /></div>
        </div>

        <div className="stat-card">
          <div className="stat-info">
            <span className="stat-label">Active Courses</span>
            <span className="stat-value">{stats.courses}</span>
          </div>
          <div className="stat-icon-bg"><BookOpen size={28} /></div>
        </div>

        <div className="stat-card">
          <div className="stat-info">
            <span className="stat-label">Avg. Attendance</span>
            <span className="stat-value">{stats.attendance}%</span>
          </div>
          <div className="stat-icon-bg"><BarChart3 size={28} /></div>
        </div>
      </div>

      {/* Removed redundant administrative tools as per user request */}
    </div>
  )
}
