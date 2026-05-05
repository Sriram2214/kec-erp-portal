import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Layout     from './components/Layout/Layout'
import ErrorBoundary from './components/ErrorBoundary'
import Splash     from './pages/Splash/Splash'
import Login      from './pages/Login/Login'
import COELogin   from './pages/Login/COELogin'
import AdminLogin  from './pages/Login/AdminLogin'
import AdminLoginPage from './pages/Login/AdminLoginPage'
import StudentLogin from './pages/Login/StudentLogin'
import FacultyLogin from './pages/Login/FacultyLogin'
import Dashboard  from './pages/Dashboard/Dashboard'
import Students   from './pages/Students/Students'
import Faculty    from './pages/Faculty/Faculty'
import RegularAttendance from './pages/Attendance/RegularAttendance'
import ESEAttendance     from './pages/Attendance/Attendance'
import RegularMarks      from './pages/Marks/RegularMarks'
import Stickers   from './pages/Stickers/Stickers'
import Results     from './pages/Results/Results'
import HallTickets from './pages/HallTickets/HallTickets'
import Security    from './pages/Security/Security'
import Master      from './pages/Master/Master'
import Courses     from './pages/Courses/Courses'
import Allocations from './pages/Allocations/Allocations'
import AcademicOps from './pages/AcademicOps/AcademicOps'
import Departments from './pages/Departments/Departments'
import ExamSchedule from './pages/ExamSchedule/ExamSchedule'
import Registration from './pages/Registration/Registration'
import Clearance    from './pages/Clearance/Clearance'
import Reports      from './pages/Reports/Reports'
import COE          from './pages/COE/COE'
import Valuation    from './pages/Valuation/Valuation'
import Certificates from './pages/Certificates/Certificates'
import COEReports   from './pages/COEReports/COEReports'
import Analytics    from './pages/Analytics/Analytics'
import './styles/index.css'
import './styles/stats.css'

function PrivateRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth()
  if (loading) return (
    <div style={{
      height: '100vh', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      color: 'var(--navy)', fontFamily: 'Cinzel, serif', fontSize: '1rem'
    }}>
      Loading…
    </div>
  )
  if (!user) return <Navigate to="/login" replace />
  
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />
  }
  
  return <Layout>{children}</Layout>
}

export default function App() {
  const [showSplash, setShowSplash] = useState(true)

  useEffect(() => {
    // Show splash for 3s on initial app load
    const timer = setTimeout(() => {
      setShowSplash(false)
    }, 3000)
    return () => clearTimeout(timer)
  }, [])

  // 1. If splash is active, show ONLY the splash (preventing background flicker)
  if (showSplash) {
    return <Splash isVisible={true} />
  }

  // 2. Once splash is done, mount the full application
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <AuthProvider>
          <Routes>
            <Route path="/"      element={<Navigate to="/login" replace />} />
            <Route path="/login"          element={<Login />} />
            <Route path="/coe-login"      element={<COELogin />} />
            <Route path="/admin-login"    element={<AdminLogin />} />
            <Route path="/student-portal" element={<StudentLogin />} />
            <Route path="/faculty-portal" element={<FacultyLogin />} />

            {/* Active pages */}
            <Route path="/dashboard"  element={<PrivateRoute><Dashboard  /></PrivateRoute>} />
            <Route path="/students"   element={<PrivateRoute allowedRoles={['admin', 'coe']}><Students   /></PrivateRoute>} />
            <Route path="/faculty"    element={<PrivateRoute allowedRoles={['admin']}><Faculty    /></PrivateRoute>} />
            <Route path="/departments" element={<PrivateRoute allowedRoles={['admin', 'coe']}><Departments /></PrivateRoute>} />
            <Route path="/attendance"  element={<PrivateRoute allowedRoles={['faculty', 'admin']}><RegularAttendance /></PrivateRoute>} />
            <Route path="/marks"       element={<PrivateRoute allowedRoles={['faculty', 'admin']}><RegularMarks /></PrivateRoute>} />
            <Route path="/ese-attendance" element={<PrivateRoute allowedRoles={['admin', 'coe']}><ESEAttendance /></PrivateRoute>} />
            <Route path="/stickers"    element={<PrivateRoute allowedRoles={['admin', 'coe']}><Stickers   /></PrivateRoute>} />
            <Route path="/results"    element={<PrivateRoute><Results    /></PrivateRoute>} />
            <Route path="/halltickets" element={<PrivateRoute><HallTickets /></PrivateRoute>} />
            <Route path="/security"    element={<PrivateRoute allowedRoles={['admin']}><Security /></PrivateRoute>} />
            <Route path="/master"      element={<PrivateRoute allowedRoles={['admin']}><Master /></PrivateRoute>} />
            <Route path="/courses"     element={<PrivateRoute allowedRoles={['admin']}><Courses /></PrivateRoute>} />
            <Route path="/allocations" element={<PrivateRoute allowedRoles={['admin']}><Allocations /></PrivateRoute>} />
            <Route path="/exam-timetable" element={<PrivateRoute allowedRoles={['admin', 'coe', 'student', 'faculty']}><ExamSchedule /></PrivateRoute>} />
            <Route path="/registration" element={<PrivateRoute allowedRoles={['student', 'admin']}><Registration /></PrivateRoute>} />
            <Route path="/clearance"   element={<PrivateRoute allowedRoles={['admin', 'coe']}><Clearance /></PrivateRoute>} />
            <Route path="/reports"     element={<PrivateRoute allowedRoles={['admin', 'coe']}><Reports /></PrivateRoute>} />
            <Route path="/coe"         element={<PrivateRoute allowedRoles={['admin', 'coe']}><COE /></PrivateRoute>} />
            <Route path="/valuation"   element={<PrivateRoute allowedRoles={['admin', 'coe']}><Valuation /></PrivateRoute>} />
            <Route path="/certificates" element={<PrivateRoute><Certificates /></PrivateRoute>} />
            <Route path="/coe-reports" element={<PrivateRoute allowedRoles={['coe', 'admin']}><COEReports /></PrivateRoute>} />
            <Route path="/analytics"   element={<PrivateRoute allowedRoles={['admin', 'coe']}><Analytics /></PrivateRoute>} />

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </ErrorBoundary>
    </BrowserRouter>
  )
}
