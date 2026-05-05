import { useState, useRef, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import api from '../../api/index'
import './Attendance.css'

const SESSION_OPTIONS = ['FN', 'AN']

const Icon = {
  Search:  () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{width:16}}><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>,
  Present: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{width:14}}><polyline points="20 6 9 17 4 12"/></svg>,
  Absent:  () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{width:14}}><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
  Warning: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{width:14}}><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
  Pdf:     () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width:16}}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>,
  Box:     () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width:16}}><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><polyline points="3.29 7 12 12 20.71 7"/><line x1="12" y1="22" x2="12" y2="12"/></svg>,
  Truck:   () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width:16}}><rect x="1" y="3" width="15" height="13"/><polyline points="16 8 20 8 23 11 23 16 16 16"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>,
  Save:    () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width:16}}><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>,
}

export default function Attendance() {
  const [courseCode,   setCourseCode]   = useState('')
  const [courseInfo,   setCourseInfo]   = useState(null)
  const [students,     setStudents]     = useState([])
  const [departments,  setDepartments]  = useState([])
  const [selDept,      setSelDept]      = useState('')
  const [searchTerm,   setSearchTerm]   = useState('')
  const [examDate,     setExamDate]     = useState('')
  const [session,      setSession]      = useState('FN')
  const [loading,      setLoading]      = useState(false)
  const [saving,       setSaving]       = useState(false)
  const [error,        setError]        = useState('')
  const [saved,        setSaved]        = useState(false)
  const [pdfLoading,   setPdfLoading]   = useState(false)
  const [coverLoading, setCoverLoading] = useState(false)
  const [despLoading,  setDespLoading]  = useState(false)
  const [dummyLoading, setDummyLoading] = useState(false)
  const [currentPage,  setCurrentPage]  = useState(1)
  const studentsPerPage = 30
  
  const [searchParams] = useSearchParams()
  const inputRef = useRef(null)

  // Auto-load if course_code in URL
  useEffect(() => {
    const code = searchParams.get('course_code')
    if (code) {
      setCourseCode(code)
      handleLoad(code)
    }
    fetchDepts()
  }, [])

  // Reset page when department filter changes
  useEffect(() => {
    setCurrentPage(1)
  }, [selDept])

  async function fetchDepts() {
    try {
      const res = await api.get('/master/departments')
      setDepartments(res.data)
    } catch (e) { console.error('Failed to fetch departments') }
  }

  /* ── Fetch course + students ───────────────────────── */
  async function handleLoad(explicitCode) {
    const code = (typeof explicitCode === 'string' ? explicitCode : courseCode).trim().toUpperCase()
    if (!code) return
    setError(''); setLoading(true); setCourseInfo(null); setStudents([]); setCurrentPage(1); setSearchTerm('')
    try {
      const res = await api.get(`/ese/students?course_code=${code}`)
      const data = res.data
      setCourseInfo(data)
      
      // Pre-fill exam date from schedule if available
      if (data.exam_date && typeof data.exam_date === 'string') {
        const parts = data.exam_date.split('.')
        if (parts.length >= 3) {
          const [dd, mm, yyyy] = parts
          setExamDate(`${yyyy.substring(0,4)}-${mm}-${dd}`)
        }
      }
      if (data.session) setSession(data.session)
      setStudents(data.students.map(s => ({ ...s })))
    } catch (e) {
      setError(e.response?.data?.message || 'Course not found. Check code and try again.')
    } finally {
      setLoading(false)
    }
  }

  /* ── Set Status ────────────────────────────────────── */
  function setStatus(id, status) {
    setStudents(prev => prev.map(s => s.id === id ? { ...s, status } : s))
    setSaved(false)
  }

  /* ── Mark all ──────────────────────────────────────── */
  function markAll(status) {
    setStudents(prev => prev.map(s => {
      if (selDept && s.department !== selDept) return s
      return { ...s, status }
    }))
    setSaved(false)
  }

  /* ── Save attendance ───────────────────────────────── */
  async function handleSave() {
    if (!courseInfo) return
    setSaving(true); setSaved(false)
    try {
      await api.post('/ese/attendance', {
        course_code: courseInfo.course_code,
        exam_date:   examDate,
        session,
        entries: students.map(s => ({ student_id: s.id, status: s.status })),
      })
      setSaved(true)
    } catch (e) {
      setError(e.response?.data?.message || 'Save failed.')
    } finally {
      setSaving(false)
    }
  }

  /* ── Download PDF ──────────────────────────────────── */
  async function downloadBlob(url, filename) {
    const res  = await api.get(url, { responseType: 'blob' })
    const burl = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
    const link = document.createElement('a')
    link.href  = burl
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(burl)
  }

  async function handlePdf() {
    if (!courseInfo) return
    setPdfLoading(true)
    try {
      const url = `/ese/attendance-pdf?course_code=${courseInfo.course_code}&department=${selDept}`
      await downloadBlob(url, `Attendance_${courseInfo.course_code}_${selDept || 'ALL'}.pdf`)
    } catch { setError('PDF generation failed.') }
    finally { setPdfLoading(false) }
  }

  async function handleCoverSheet() {
    if (!courseInfo) return
    setCoverLoading(true)
    try { await downloadBlob(`/ese/cover-sheet-pdf?course_code=${courseInfo.course_code}`, `ESE_CoverSheet_${courseInfo.course_code}.pdf`) }
    catch { setError('Cover Sheet PDF generation failed.') }
    finally { setCoverLoading(false) }
  }

  async function handleDespatch() {
    if (!courseInfo) return
    setDespLoading(true)
    try { await downloadBlob(`/ese/despatch-pdf?course_code=${courseInfo.course_code}`, `ESE_Despatch_${courseInfo.course_code}.pdf`) }
    catch { setError('Despatch PDF generation failed.') }
    finally { setDespLoading(false) }
  }

  async function handleCourierSheet() {
    if (!courseInfo) return
    setDespLoading(true)
    try { await downloadBlob(`/coe/courier-sheet?course_code=${courseInfo.course_code}`, `Courier_Sheet_${courseInfo.course_code}.pdf`) }
    catch { setError('Courier Sheet generation failed.') }
    finally { setDespLoading(false) }
  }

  async function handleGenerateDummies() {
    if (!courseInfo) return
    setDummyLoading(true)
    try {
      const res = await api.post('/coe/generate-dummies', { course_code: courseInfo.course_code })
      setSaved(false)
      alert(res.data.message)
      handleLoad()
    } catch (e) {
      alert(e.response?.data?.message || 'Failed to generate dummy numbers.')
    } finally {
      setDummyLoading(false)
    }
  }

  const filteredStudents = students.filter(s => {
    const matchesDept = !selDept || s.department === selDept
    const matchesSearch = !searchTerm || 
      s.register_number.includes(searchTerm) || 
      s.name.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesDept && matchesSearch
  })

  const absentCount  = filteredStudents.filter(s => s.status === 'Absent').length
  const presentCount = filteredStudents.filter(s => s.status === 'Present').length
  const mpCount      = filteredStudents.filter(s => s.status === 'Malpractice').length

  const totalPages = Math.ceil(filteredStudents.length / studentsPerPage)
  const pagedStudents = filteredStudents.slice((currentPage - 1) * studentsPerPage, currentPage * studentsPerPage)

  return (
    <div className="ese-page fade-in">
      {/* ── Page Header ── */}
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › ESE Attendance</div>
        <div className="page-title">ESE Attendance Sheet</div>
        <div className="page-sub">End Semester Examination — Attendance Entry</div>
      </div>

      {/* ── Course Code Search ── */}
      <div className="card ese-search-card">
        <div className="card-title">
          <Icon.Pdf />
          <span>Load by Course Code</span>
        </div>
        <div className="ese-search-row">
          <div className="ese-input-wrap">
            <label>COURSE CODE</label>
            <input
              ref={inputRef}
              type="text"
              className="ese-code-input"
              placeholder="e.g. GE241203"
              value={courseCode}
              onChange={e => { setCourseCode(e.target.value.toUpperCase()); setError('') }}
              onKeyDown={e => e.key === 'Enter' && handleLoad()}
            />
          </div>
          <button
            className="btn btn-gold ese-load-btn"
            onClick={handleLoad}
            disabled={loading || !courseCode.trim()}
          >
            {loading ? (
              <span className="ese-spinner" />
            ) : (
              <><Icon.Search /> Load Students</>
            )}
          </button>
        </div>
        {error && <div className="ese-error">⚠ {error}</div>}
      </div>

      {/* ── Course Info (auto-populated) ── */}
      {courseInfo && (
        <div className="card ese-info-card">
          <div className="ese-info-grid">
            <div className="ese-info-item">
              <span className="ese-info-label">Course Code</span>
              <span className="ese-info-val gold">{courseInfo.course_code}</span>
            </div>
            <div className="ese-info-item">
              <span className="ese-info-label">Course Title</span>
              <span className="ese-info-val">{courseInfo.course_title}</span>
            </div>
            <div className="ese-info-item">
              <span className="ese-info-label">Department</span>
              <span className="ese-info-val">{courseInfo.department}</span>
            </div>
            <div className="ese-info-item">
              <span className="ese-info-label">Semester</span>
              <span className="ese-info-val">{courseInfo.semester}</span>
            </div>
            <div className="ese-info-item">
              <span className="ese-info-label">Exam Date</span>
              <input
                type="date"
                className="ese-date-input"
                value={examDate}
                onChange={e => setExamDate(e.target.value)}
              />
            </div>
            <div className="ese-info-item">
              <span className="ese-info-label">Session</span>
              <div className="ese-session-toggle">
                {SESSION_OPTIONS.map(opt => (
                  <button
                    key={opt}
                    className={`ese-session-btn${session === opt ? ' active' : ''}`}
                    onClick={() => setSession(opt)}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Attendance Table ── */}
      {students.length > 0 && (
        <>
          {/* Toolbar */}
          <div className="ese-toolbar">
            <div className="ese-counts">
              <span className="ese-count present"><Icon.Present /> Present: <strong>{presentCount}</strong></span>
              <span className="ese-count absent"><Icon.Absent /> Absent: <strong>{absentCount}</strong></span>
              {mpCount > 0 && <span className="ese-count mp"><Icon.Warning /> MP: <strong>{mpCount}</strong></span>}
              <span className="ese-count total">Total: <strong>{filteredStudents.length}</strong></span>
            </div>
            <div className="ese-actions">
              <button className="btn btn-sm btn-green" onClick={() => markAll('Present')}>
                <Icon.Present /> All Present
              </button>
              <button className="btn btn-sm btn-red" onClick={() => markAll('Absent')}>
                <Icon.Absent /> All Absent
              </button>
              
              <div className="ese-pdf-selector">
                <select 
                  className="ese-dept-select" 
                  value={selDept} 
                  onChange={e => setSelDept(e.target.value)}
                >
                  <option value="">All Departments</option>
                  {departments.map(d => (
                    <option key={d.id} value={d.code}>{d.code}</option>
                  ))}
                </select>
                <div className="ese-search-box">
                  <Icon.Search />
                  <input 
                    type="text" 
                    placeholder="Search name/reg..." 
                    value={searchTerm}
                    onChange={e => { setSearchTerm(e.target.value); setCurrentPage(1) }}
                  />
                </div>
                <button className="btn btn-sm btn-outline" onClick={handlePdf} disabled={pdfLoading}>
                  {pdfLoading ? '⏳…' : <><Icon.Pdf /> Att. PDF</>}
                </button>
              </div>

              <button className="btn btn-sm btn-outline ese-cover-btn" onClick={handleCoverSheet} disabled={coverLoading}>
                {coverLoading ? '⏳…' : <><Icon.Box /> Cover Sheet</>}
              </button>
              <button className="btn btn-sm ese-desp-btn" onClick={handleDespatch} disabled={despLoading}>
                {despLoading ? '⏳…' : <><Icon.Truck /> Despatch</>}
              </button>
              <button className="btn btn-sm btn-outline" onClick={handleCourierSheet} disabled={despLoading}>
                <Icon.Truck /> Courier Sheet
              </button>
              <button className="btn btn-gold btn-sm" onClick={handleSave} disabled={saving}>
                {saving ? '⏳…' : saved ? '✓ Saved!' : <><Icon.Save /> Save</>}
              </button>
              <button className="btn btn-sm btn-outline" onClick={handleGenerateDummies} disabled={dummyLoading}>
                {dummyLoading ? '⏳…' : 'Generate Dummies'}
              </button>
            </div>
          </div>

          {/* Table */}
          <div className="card ese-table-card">
            <table className="ese-table">
              <thead>
                <tr>
                  <th style={{ width: '8%' }}>S.No</th>
                  <th style={{ width: '22%' }}>Reg. No</th>
                  <th style={{ width: '50%' }}>Name of Student</th>
                  <th style={{ width: '20%', textAlign: 'center' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {pagedStudents.map((s, idx) => {
                  const realIndex = (currentPage - 1) * studentsPerPage + idx + 1
                  return (
                    <tr 
                      key={s.id} 
                      className={
                        s.status === 'Absent' ? 'ese-row-absent' : 
                        s.status === 'Malpractice' ? 'ese-row-malpractice' : ''
                      }
                    >
                      <td className="ese-sno">{realIndex}</td>
                      <td className="ese-regno">{s.register_number}</td>
                      <td className="ese-name">{s.name}</td>
                      <td className="ese-status-cell">
                        <div className="status-segmented">
                          <button 
                            className={`status-btn present ${s.status === 'Present' ? 'active' : ''}`}
                            onClick={() => setStatus(s.id, 'Present')}
                            title="Present"
                          >
                            P
                          </button>
                          <button 
                            className={`status-btn absent ${s.status === 'Absent' ? 'active' : ''}`}
                            onClick={() => setStatus(s.id, 'Absent')}
                            title="Absent"
                          >
                            A
                          </button>
                          <button 
                            className={`status-btn malpractice ${s.status === 'Malpractice' ? 'active' : ''}`}
                            onClick={() => setStatus(s.id, 'Malpractice')}
                            title="Malpractice"
                          >
                            MP
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="ese-pagination">
                <button 
                  className="btn btn-sm btn-outline" 
                  disabled={currentPage === 1}
                  onClick={() => { setCurrentPage(prev => prev - 1); window.scrollTo(0, 0) }}
                >
                  Previous
                </button>
                <span className="ese-page-info">Page <strong>{currentPage}</strong> of {totalPages}</span>
                <button 
                  className="btn btn-sm btn-outline" 
                  disabled={currentPage === totalPages}
                  onClick={() => { setCurrentPage(prev => prev + 1); window.scrollTo(0, 0) }}
                >
                  Next
                </button>
              </div>
            )}
          </div>

          {/* Bottom Save */}
          <div className="ese-bottom-bar">
            <div className="ese-counts">
              <span className="ese-count present"><Icon.Present /> <strong>{presentCount}</strong></span>
              <span className="ese-count absent"><Icon.Absent /> <strong>{absentCount}</strong></span>
              {mpCount > 0 && <span className="ese-count mp"><Icon.Warning /> <strong>{mpCount}</strong></span>}
            </div>
            <div style={{ display: 'flex', gap: '0.8rem', flexWrap: 'wrap' }}>
              <button className="btn btn-outline" onClick={handlePdf} disabled={pdfLoading}>
                {pdfLoading ? '⏳…' : <><Icon.Pdf /> Att. PDF</>}
              </button>
              <button className="btn ese-desp-btn" onClick={handleDespatch} disabled={despLoading}>
                {despLoading ? '⏳…' : <><Icon.Truck /> Despatch PDF</>}
              </button>
              <button className="btn btn-gold" onClick={handleSave} disabled={saving}>
                {saving ? '⏳…' : saved ? '✓ Saved!' : <><Icon.Save /> Save</>}
              </button>
            </div>
          </div>
        </>
      )}

      {/* Empty state */}
      {!loading && courseInfo && students.length === 0 && (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>
          No students found for semester {courseInfo.semester}.
        </div>
      )}
    </div>
  )
}
