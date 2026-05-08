import { useState, useEffect, lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Layout     from './components/Layout/Layout'
import ErrorBoundary from './components/ErrorBoundary'
import Splash     from './pages/Splash/Splash'

// Critical pages - Eager Load
import Login      from './pages/Login/Login'
import Dashboard  from './pages/Dashboard/Dashboard'

// Non-critical / Heavy pages - Lazy Load
const COELogin   = lazy(() => import('./pages/Login/COELogin'))
const AdminLogin  = lazy(() => import('./pages/Login/AdminLogin'))
const AdminLoginPage = lazy(() => import('./pages/Login/AdminLoginPage'))
const StudentLogin = lazy(() => import('./pages/Login/StudentLogin'))
const FacultyLogin = lazy(() => import('./pages/Login/FacultyLogin'))
const Students   = lazy(() => import('./pages/Students/Students'))
const Faculty    = lazy(() => import('./pages/Faculty/Faculty'))
const RegularAttendance = lazy(() => import('./pages/Attendance/RegularAttendance'))
const ESEAttendance     = lazy(() => import('./pages/Attendance/Attendance'))
const RegularMarks      = lazy(() => import('./pages/Marks/RegularMarks'))
const Stickers   = lazy(() => import('./pages/Stickers/Stickers'))
const Results     = lazy(() => import('./pages/Results/Results'))
const HallTickets = lazy(() => import('./pages/HallTickets/HallTickets'))
const Security    = lazy(() => import('./pages/Security/Security'))
const Master      = lazy(() => import('./pages/Master/Master'))
const Courses     = lazy(() => import('./pages/Courses/Courses'))
const Allocations = lazy(() => import('./pages/Allocations/Allocations'))
const AcademicOps = lazy(() => import('./pages/AcademicOps/AcademicOps'))
const Departments = lazy(() => import('./pages/Departments/Departments'))
import ExamSchedule from './pages/Schedules/ExamSchedule'
const Registration = lazy(() => import('./pages/Registration/Registration'))
const Clearance    = lazy(() => import('./pages/Clearance/Clearance'))
const Reports      = lazy(() => import('./pages/Reports/Reports'))
const COE          = lazy(() => import('./pages/COE/COE'))
const Valuation    = lazy(() => import('./pages/Valuation/Valuation'))
const Certificates = lazy(() => import('./pages/Certificates/Certificates'))
const COEReports   = lazy(() => import('./pages/COEReports/COEReports'))
const Analytics    = lazy(() => import('./pages/Analytics/Analytics'))

import './styles/index.css'
import './styles/stats.css'

const PageLoader = () => (
  <div style={{ height: '80vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--navy)', fontFamily: 'Cinzel, serif', letterSpacing: '0.2em' }}>
    <div className="analytics-spinner" style={{ marginBottom: '1.5rem' }} />
    <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>LOADING...</div>
  </div>
)

function PrivateRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth()
  if (loading) return <PageLoader />
  if (!user) return <Navigate to="/login" replace />
  
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />
  }
  
  return <Layout><Suspense fallback={<PageLoader />}>{children}</Suspense></Layout>
}

import { MasterProvider } from './context/MasterContext'
import { ToastProvider } from './components/Toast/Toast'

export default function App() {
  const [showSplash, setShowSplash] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowSplash(false)
    }, 1000)
    return () => clearTimeout(timer)
  }, [])

  if (showSplash) {
    return <Splash isVisible={true} />
  }

  return (
    <BrowserRouter>
      <ErrorBoundary>
        <AuthProvider>
          <ToastProvider>
            <MasterProvider>
              <Routes>
              <Route path="/"      element={<Navigate to="/login" replace />} />
              <Route path="/login"          element={<Suspense fallback={<PageLoader />}><Login /></Suspense>} />
              <Route path="/coe-login"      element={<Suspense fallback={<PageLoader />}><COELogin /></Suspense>} />
              <Route path="/admin-login"    element={<Suspense fallback={<PageLoader />}><AdminLogin /></Suspense>} />
              <Route path="/student-portal" element={<Suspense fallback={<PageLoader />}><StudentLogin /></Suspense>} />
              <Route path="/faculty-portal" element={<Suspense fallback={<PageLoader />}><FacultyLogin /></Suspense>} />

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
              <Route path="/exam-timetable" element={<PrivateRoute allowedRoles={['admin', 'coe', 'student', 'faculty']}><ExamSchedule /></PrivateRoute>} /> {/* v2.1 */}
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
            </MasterProvider>
          </ToastProvider>
        </AuthProvider>
      </ErrorBoundary>
    </BrowserRouter>
  )
}
