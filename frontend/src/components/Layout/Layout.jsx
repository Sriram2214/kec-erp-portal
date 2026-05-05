import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { 
  LogOut, LayoutDashboard, Users, UserRound, BookOpen, 
  Calendar, CheckSquare, FileEdit, Ticket, Tags, BarChart3, 
  ShieldAlert, Database, ClipboardCheck, PieChart, GraduationCap,
  BookCheck, ScrollText, CheckCircle, ChevronRight, Building2
} from 'lucide-react'
import './Layout.css'

const Icon = {
  Dashboard:   LayoutDashboard,
  Students:    Users,
  Faculty:     UserRound,
  Courses:     BookOpen,
  Schedule:    Calendar,
  Attendance:  CheckSquare,
  Marks:       FileEdit,
  HallTickets: Ticket,
  Stickers:    Tags,
  Results:     BarChart3,
  Security:    ShieldAlert,
  Master:      Database,
  Reg:         ClipboardCheck,
  Clearance:   CheckCircle,
  Reports:     PieChart,
  COE:         GraduationCap,
  Valuation:   BookCheck,
  Cert:        ScrollText,
}

// ── Navigation Workspaces ──────────────────────────────────────────
const SECTIONS = [
  {
    title: "General",
    roles: ['admin', 'coe', 'faculty', 'student'],
    items: [
      { to: '/dashboard', icon: Icon.Dashboard, label: 'Dashboard' }
    ]
  },
  {
    title: "Academic Operations",
    roles: ['admin', 'coe'],
    items: [
      { to: '/students',    icon: Icon.Students,  label: 'Student Records' },
      { to: '/ese-attendance', icon: Icon.Attendance, label: 'Exam Attendance' },
    ]
  },
  {
    title: "COE Command Center",
    roles: ['admin', 'coe'],
    items: [
      { to: '/exam-timetable', icon: Icon.Schedule,    label: 'Examination Schedule' },
      { to: '/coe-reports',    icon: Icon.Reports,     label: 'End Sem Reports' },
      { to: '/coe',            icon: Icon.COE,         label: 'COE Operations' },
      { to: '/valuation',      icon: Icon.Valuation,   label: 'Valuation & Grades' },
      { to: '/halltickets',    icon: Icon.HallTickets, label: 'Hall Tickets' },
      { to: '/results',        icon: Icon.Results,     label: 'Results & Analytics' },
      { to: '/stickers',       icon: Icon.Stickers,    label: 'Exam Stickers' },
      { to: '/clearance',      icon: Icon.Clearance,   label: 'Exam Clearance' },
    ]
  },
  {
    title: "Faculty Workspace",
    roles: ['faculty'],
    items: [
      { to: '/attendance', icon: Icon.Attendance, label: 'Attendance Entry' },
      { to: '/marks',      icon: Icon.Marks,      label: 'Internal Marks' },
      { to: '/results',    icon: Icon.Results,    label: 'Class Results' },
    ]
  },
  {
    title: "Student Portal",
    roles: ['student'],
    items: [
      { to: '/registration', icon: Icon.Reg,         label: 'Exam Registration' },
      { to: '/halltickets',  icon: Icon.HallTickets, label: 'My Hall Ticket' },
      { to: '/results',      icon: Icon.Results,     label: 'My Results' },
      { to: '/certificates', icon: Icon.Cert,        label: 'Digital Certificates' },
    ]
  }
];

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [expandedSections, setExpandedSections] = useState([])

  const toggleSection = (id) => {
    setExpandedSections(prev => 
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    )
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-left">
          <div className="header-logo">
            <img src="/logo.png" alt="KEC" />
          </div>
          <div className="header-text">
            <div className="header-title">Kings Engineering College</div>
            <div className="header-subtitle">Examination Management System · Chennai</div>
          </div>
        </div>

        <div className="header-right">
          <div className="user-badge">
            <div className="user-info">
              <div className="user-name">{user?.username}</div>
              <div className="user-role">{user?.role?.toUpperCase()} Portal</div>
            </div>
            <div className="user-avatar">{user?.username?.[0]?.toUpperCase()}</div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <LogOut size={16} /> Logout
          </button>
        </div>
      </header>

      <div className="app-body">
        <aside className="sidebar">
          {SECTIONS.filter(section => section.roles.includes(user?.role)).map((section, idx) => (
            <div key={idx} className="sidebar-section">
              <div className="sidebar-section-title">{section.title}</div>
              <div className="section-content fade-in">
                {section.items.map(item => {
                  if (item.isCollapsible) {
                    const isExpanded = expandedSections.includes(item.id);
                    return (
                      <div key={item.id} className="collapsible-nav-item">
                        <div 
                          className={`nav-item ${isExpanded ? 'active-parent' : ''}`}
                          onClick={() => toggleSection(item.id)}
                        >
                          <span className="nav-icon"><item.icon size={18} /></span>
                          <span className="nav-label">{item.title}</span>
                          <ChevronRight 
                            className="nav-chevron" 
                            size={14} 
                            style={{ 
                              opacity: 1,
                              transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
                              transition: 'transform 0.2s ease'
                            }} 
                          />
                        </div>
                        {isExpanded && (
                          <div className="sub-menu fade-in">
                            {item.items.map(sub => (
                              <NavLink
                                key={sub.to}
                                to={sub.to}
                                className={({ isActive }) =>
                                  `sub-nav-item${isActive ? ' active' : ''}`
                                }
                              >
                                <span className="sub-nav-dot" />
                                <span className="nav-label">{sub.label}</span>
                              </NavLink>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  }
                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      className={({ isActive }) =>
                        `nav-item${isActive ? ' active' : ''}`
                      }
                    >
                      <span className="nav-icon"><item.icon size={18} /></span>
                      <span className="nav-label">{item.label}</span>
                      <ChevronRight className="nav-chevron" size={14} />
                    </NavLink>
                  );
                })}
              </div>
            </div>
          ))}
        </aside>

        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  )
}
