import { useState, useEffect } from 'react'
import api from '../../api/index'
import { useAuth } from '../../context/AuthContext'
import './HallTickets.css'

const Icon = {
  Download: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width:18}}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>,
  Search: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{width:16}}><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>,
  Info: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width:18}}><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>,
}

export default function HallTickets() {
  const { user } = useAuth()
  const [regno, setRegno] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const isStudent = user?.role === 'student'

  async function handleDownload() {
    const code = isStudent ? '' : regno.trim().toUpperCase()
    if (!isStudent && !code) {
      setError('Please enter a register number.'); return
    }

    setError(''); setLoading(true)
    try {
      const res = await api.get(`/ese/hallticket-pdf${code ? '?regno='+code : ''}`, { 
        responseType: 'blob' 
      })
      const url  = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href  = url
      link.download = `HallTicket_${code || user?.username || 'Student'}.pdf`
      link.click()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      let msg = 'Hall Ticket not found or not yet generated for this student.'
      if (e.response?.data?.message) msg = e.response.data.message
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="ht-page fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Hall Tickets</div>
        <div className="page-title">Hall Ticket Generation</div>
        <div className="page-sub">Download official exam hall tickets with schedule</div>
      </div>

      <div className="ht-container">
        <div className="card ht-card">
          <div className="card-title">
            <Icon.Download />
            <span>{isStudent ? 'Your Hall Ticket' : 'Download Hall Ticket'}</span>
          </div>
          
          <div className="ht-search">
            {isStudent ? (
              <div className="ht-student-view">
                <p className="ht-hint">Download your official Hall Ticket for the current examination session.</p>
                <button 
                  className="btn btn-gold ht-btn-large" 
                  onClick={handleDownload}
                  disabled={loading}
                >
                  {loading ? <span className="ht-spinner" /> : <><Icon.Download /> Download Hall Ticket PDF</>}
                </button>
              </div>
            ) : (
              <>
                <p className="ht-hint">Enter Register Number to download the hall ticket.</p>
                <div className="ht-input-row">
                  <input 
                    type="text" 
                    className="ht-input" 
                    placeholder="Register Number" 
                    value={regno}
                    onChange={e => setRegno(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleDownload()}
                  />
                  <button 
                    className="btn btn-gold ht-btn" 
                    onClick={handleDownload}
                    disabled={loading}
                  >
                    {loading ? <span className="ht-spinner" /> : <><Icon.Download /> Download</>}
                  </button>
                </div>
              </>
            )}
            {error && <div className="ht-error">⚠ {error}</div>}
          </div>
        </div>


        <div className="card ht-instructions">
          <div className="card-title">
            <Icon.Info />
            <span>Important Instructions</span>
          </div>
          <ul className="ht-list">
            <li>Carry a printed copy of the Hall Ticket to the examination hall.</li>
            <li>Verify your Name, Degree, Branch, and Exam Schedule.</li>
            <li>In case of any discrepancy, contact the Controller of Examinations immediately.</li>
            <li>Report to the exam venue at least 30 minutes before the session starts.</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
