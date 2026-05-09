import { useState, useRef } from 'react'
import api from '../../api/index'
import './Stickers.css'

const Icon = {
  Upload:  () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width:18}}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>,
  Excel:   () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width:18}}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>,
  Search:  () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{width:16}}><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>,
  Calendar:() => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width:18}}><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>,
  Tag:     () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width:14}}><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>,
  Check:   () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{width:16}}><polyline points="20 6 9 17 4 12"/></svg>,
  Warning: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width:16}}><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
  Info:    () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width:18}}><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>,
}

export default function Stickers() {
  const [date,         setDate]         = useState('')
  const [courses,      setCourses]      = useState([])
  const [dateLoading,  setDateLoading]  = useState(false)
  const [dateError,    setDateError]    = useState('')

  // Upload state
  const [uploading,    setUploading]    = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [uploadError,  setUploadError]  = useState('')
  const fileRef = useRef(null)

  // Per-course sticker loading
  const [stickerLoading, setStickerLoading] = useState({})

  /* ── Load courses by date ───────────────────────── */
  async function handleDateSearch() {
    if (!date) return
    setDateError(''); setCourses([]); setDateLoading(true)
    try {
      const res = await api.get(`/ese/courses-by-date?date=${date}`)
      setCourses(res.data)
      if (res.data.length === 0) setDateError('No exams scheduled on this date.')
    } catch (e) {
      setDateError(e.response?.data?.message || 'Failed to load courses.')
    } finally {
      setDateLoading(false)
    }
  }

  /* ── Download Sticker PDF ───────────────────────── */
  async function handleSticker(id, code) {
    setStickerLoading(p => ({ ...p, [code]: true }))
    try {
      const res = await api.get(
        `/ese/sticker-pdf?course_id=${id}`,
        { responseType: 'blob' }
      )
      const url  = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href  = url
      link.download = `ESE_Stickers_${code}.pdf`
      link.click()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      let msg = 'Sticker PDF failed.'
      if (e.response?.data) {
        // blob → text
        try {
          const text = await e.response.data.text()
          const json = JSON.parse(text)
          msg = json.message || msg
        } catch {}
      }
      alert(msg)
    } finally {
      setStickerLoading(p => ({ ...p, [code]: false }))
    }
  }

  /* ── Upload dummy numbers ───────────────────────── */
  async function handleUpload() {
    const file = fileRef.current?.files[0]
    if (!file) return
    setUploading(true); setUploadResult(null); setUploadError('')
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await api.post('/ese/dummy-upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setUploadResult(res.data)
      if (fileRef.current) fileRef.current.value = ''
      // Refresh course list
      if (date) handleDateSearch()
    } catch (e) {
      setUploadError(e.response?.data?.message || 'Upload failed.')
    } finally {
      setUploading(false)
    }
  }

  /* ── Download template ──────────────────────────── */
  async function handleTemplate() {
    const res = await api.get('/ese/dummy-template', { responseType: 'blob' })
    const url  = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href  = url
    link.download = 'Dummy_Upload_Template.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="stk-page fade-in">
      {/* ── Header ── */}
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Exam Stickers</div>
        <div className="page-title">Dummy Sticker Manager</div>
        <div className="page-sub">Upload dummy numbers & generate answer-script stickers</div>
      </div>

      <div className="stk-layout">

        {/* ── Left Panel: Upload ── */}
        <div className="stk-left">
          <div className="card">
            <div className="card-title"><Icon.Upload /> Upload Dummy Numbers</div>
            <p className="stk-hint">
              Excel format: <strong>REGNO | DUMMY NO | FOIL NO | COURSE CODE</strong>
            </p>

            <div className="stk-upload-zone"
              onClick={() => fileRef.current?.click()}
              onDragOver={e => e.preventDefault()}
              onDrop={e => { e.preventDefault(); if (e.dataTransfer.files[0]) { fileRef.current.files = e.dataTransfer.files; } }}
            >
              <div className="stk-upload-icon"><Icon.Excel /></div>
              <div className="stk-upload-text">
                {fileRef.current?.files[0]?.name || 'Click or drag Excel file here'}
              </div>
              <input
                ref={fileRef}
                type="file"
                accept=".xlsx,.xls"
                style={{ display: 'none' }}
                onChange={() => setUploadResult(null)}
              />
            </div>

            <div className="stk-upload-actions">
              <button className="btn btn-outline btn-sm" onClick={handleTemplate}>
                <Icon.Excel /> Download Template
              </button>
              <button
                className="btn btn-gold"
                onClick={handleUpload}
                disabled={uploading}
              >
                {uploading ? '⏳ Uploading…' : <><Icon.Upload /> Upload</>}
              </button>
            </div>

            {uploadError && (
              <div className="stk-error"><Icon.Warning /> {uploadError}</div>
            )}

            {uploadResult && (
              <div className="stk-success">
                <div><Icon.Check /> {uploadResult.message}</div>
                <div className="stk-upload-stats">
                  <span className="badge badge-green">Added: {uploadResult.added}</span>
                  <span className="badge badge-gold">Skipped: {uploadResult.skipped}</span>
                </div>
                {uploadResult.errors?.length > 0 && (
                  <details className="stk-errors-detail">
                    <summary>{uploadResult.errors.length} row error(s)</summary>
                    <ul>{uploadResult.errors.map((e, i) => <li key={i}>{e}</li>)}</ul>
                  </details>
                )}
              </div>
            )}
          </div>
        </div>

        {/* ── Right Panel: Date + Course List ── */}
        <div className="stk-right">
          <div className="card">
            <div className="card-title"><Icon.Calendar /> Select Exam Date</div>
            <div className="stk-date-row">
              <input
                type="date"
                className="stk-date-input"
                value={date}
                onChange={e => { setDate(e.target.value); setDateError(''); setCourses([]) }}
                onKeyDown={e => e.key === 'Enter' && handleDateSearch()}
              />
              <button
                className="btn btn-gold"
                onClick={handleDateSearch}
                disabled={dateLoading || !date}
              >
                {dateLoading ? <span className="stk-spinner" /> : <><Icon.Search /> Load Courses</>}
              </button>
            </div>
            {dateError && <div className="stk-error">{dateError}</div>}
          </div>

          {/* Course list */}
          {courses.length > 0 && (
            <div className="card stk-course-card">
              <div className="card-title">
                <Icon.Excel />
                <span>Courses on {new Date(date + 'T00:00:00').toLocaleDateString('en-IN', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' })}</span>
                <span className="badge badge-blue">{courses.length} course{courses.length > 1 ? 's' : ''}</span>
              </div>

              <table className="stk-table">
                <thead>
                  <tr>
                    <th>Course Code</th>
                    <th>Course Title</th>
                    <th>Dept</th>
                    <th>Session</th>
                    <th style={{ textAlign: 'center' }}>Stickers</th>
                    <th style={{ textAlign: 'center' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {courses.map(c => (
                    <tr key={c.schedule_id}>
                      <td><span className="stk-code">{c.course_code}</span></td>
                      <td className="stk-title">{c.course_title}</td>
                      <td><span className="badge badge-blue">{c.department}</span></td>
                      <td>
                        <span className={`badge ${c.session === 'FN' ? 'badge-gold' : 'badge-blue'}`}>
                          {c.session}
                        </span>
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        {c.sticker_count > 0 ? (
                          <span className="badge badge-green">{c.sticker_count} uploaded</span>
                        ) : (
                          <span className="badge badge-red">No data</span>
                        )}
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <button
                          className={`btn btn-sm stk-btn ${c.sticker_count === 0 ? 'stk-btn-disabled' : ''}`}
                          onClick={() => handleSticker(c.course_id, c.course_code)}
                          disabled={stickerLoading[c.course_code] || c.sticker_count === 0}
                          title={c.sticker_count === 0 ? 'Upload dummy numbers first' : 'Generate Sticker PDF'}
                        >
                          {stickerLoading[c.course_code] ? (
                            <span className="stk-spinner" />
                          ) : (
                            <><Icon.Tag /> Sticker</>
                          )}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* How-to guide */}
          {courses.length === 0 && !dateLoading && (
            <div className="card" style={{ marginTop: 0 }}>
              <div className="card-title"><Icon.Info /> How to use</div>
              <ol className="stk-steps">
                <li>Upload dummy numbers Excel (REGNO | DUMMY NO | FOIL NO | COURSE CODE)</li>
                <li>Select an exam date above</li>
                <li>All courses scheduled on that date will appear</li>
                <li>Click <strong>🏷 Sticker</strong> to download the sticker PDF</li>
              </ol>
              <div className="stk-note">
                <Icon.Warning /> Sticker PDF excludes <strong>Absent</strong> and <strong>Malpractice</strong> students automatically.
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}
