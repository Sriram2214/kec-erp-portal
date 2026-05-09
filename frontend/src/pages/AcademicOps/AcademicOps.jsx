import { useEffect, useState } from 'react'
import api from '../../api/index'

import './AcademicOps.css'

export default function AcademicOps() {
  const [activeTab, setActiveTab] = useState('grades')
  const [grades, setGrades] = useState([])
  const [timetable, setTimetable] = useState([])
  const [master, setMaster] = useState({ batches: [] })
  const [allocs, setAllocs] = useState([])
  
  const [selBatch, setSelBatch] = useState('')
  const [selSection, setSelSection] = useState('A')

  const loadGrades = () => api.get('/academic/grades').then(r => setGrades(r.data))
  const loadTimetable = () => {
    if (!selBatch) return
    api.get(`/academic/timetable?batch=${selBatch}&section=${selSection}`)
      .then(r => setTimetable(r.data))
  }

  useEffect(() => {
    loadGrades()
    api.get('/master').then(r => {
      setMaster(r.data)
      if (r.data.batches.length > 0) setSelBatch(r.data.batches[0].label)
    })
    api.get('/allocations').then(r => setAllocs(r.data))
  }, [])

  useEffect(() => { loadTimetable() }, [selBatch, selSection])

  const handleUpdateGrades = async () => {
    await api.post('/academic/grades', grades)
    alert('Grade scale updated!')
  }

  const handleAddPeriod = async (day, period, allocId) => {
    if (!allocId) return
    await api.post('/academic/timetable', {
      allocation_id: allocId,
      day_of_week: day,
      period: period
    })
    loadTimetable()
  }

  const handleDeletePeriod = async (id) => {
    await api.delete(`/academic/timetable/${id}`)
    loadTimetable()
  }

  const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const PERIODS = [1, 2, 3, 4, 5, 6, 7, 8]

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Academic Operations</div>
        <div className="page-title">Academic Controls</div>
        <div className="page-sub">Phase 3: Grades Configuration & Timetable Management</div>
      </div>

      <div className="master-tabs">
        <button className={`master-tab ${activeTab === 'grades' ? 'active' : ''}`} onClick={() => setActiveTab('grades')}>Grade Scale</button>
        <button className={`master-tab ${activeTab === 'timetable' ? 'active' : ''}`} onClick={() => setActiveTab('timetable')}>Class Timetable</button>
      </div>

      {activeTab === 'grades' ? (
        <div className="card">
          <div className="card-title">Grade Scale (Item 9)</div>
          <table className="master-table">
            <thead>
              <tr><th>Grade</th><th>Min Mark</th><th>Max Mark</th><th>Points</th></tr>
            </thead>
            <tbody>
              {grades.map((g, i) => (
                <tr key={i}>
                  <td><input value={g.grade} onChange={e => {
                    const n = [...grades]; n[i].grade = e.target.value; setGrades(n)
                  }} /></td>
                  <td><input type="number" value={g.min_mark} onChange={e => {
                    const n = [...grades]; n[i].min_mark = parseInt(e.target.value); setGrades(n)
                  }} /></td>
                  <td><input type="number" value={g.max_mark} onChange={e => {
                    const n = [...grades]; n[i].max_mark = parseInt(e.target.value); setGrades(n)
                  }} /></td>
                  <td><input type="number" value={g.points} onChange={e => {
                    const n = [...grades]; n[i].points = parseInt(e.target.value); setGrades(n)
                  }} /></td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
            <button className="btn btn-gold" onClick={handleUpdateGrades}>Save Configuration</button>
            <button className="btn btn-outline" onClick={() => setGrades([...grades, {grade:'', min_mark:0, max_mark:0, points:0}])}>+ Add Row</button>
          </div>
        </div>
      ) : (
        <>
          <div className="filter-bar card">
            <div className="filter-row">
              <select value={selBatch} onChange={e => setSelBatch(e.target.value)}>
                {master.groupedBatches?.ug.length > 0 && (
                  <>
                    <option disabled>── UG Batches (4 Years) ──</option>
                    {master.groupedBatches.ug.map(b => <option key={b.id} value={b.label}>{b.label}</option>)}
                  </>
                )}
                {master.groupedBatches?.pg.length > 0 && (
                  <>
                    <option disabled>── PG Batches (2 Years) ──</option>
                    {master.groupedBatches.pg.map(b => <option key={b.id} value={b.label}>{b.label}</option>)}
                  </>
                )}
                {master.groupedBatches?.phd.length > 0 && (
                  <>
                    <option disabled>── PhD / Research ──</option>
                    {master.groupedBatches.phd.map(b => <option key={b.id} value={b.label}>{b.label}</option>)}
                  </>
                )}
                {master.groupedBatches?.other.length > 0 && (
                  <>
                    <option disabled>── Other Batches ──</option>
                    {master.groupedBatches.other.map(b => <option key={b.id} value={b.label}>{b.label}</option>)}
                  </>
                )}
              </select>
              <select value={selSection} onChange={e => setSelSection(e.target.value)}>
                <option>A</option><option>B</option><option>C</option>
              </select>
            </div>
          </div>

          <div className="card timetable-card">
            <div className="timetable-container">
              <table className="timetable-table">
                <thead>
                  <tr>
                    <th>Day</th>
                    {PERIODS.map(p => <th key={p}>P{p}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {DAYS.map(day => (
                    <tr key={day}>
                      <td className="day-name"><strong>{day}</strong></td>
                      {PERIODS.map(p => {
                        const entry = timetable.find(e => e.day === day && e.period === p)
                        return (
                          <td key={p} className="period-cell">
                            {entry ? (
                              <div className="tt-entry">
                                <div className="tt-code">{entry.course_code}</div>
                                <div className="tt-faculty">{entry.faculty_name}</div>
                                <button className="tt-del" onClick={() => handleDeletePeriod(entry.id)}>×</button>
                              </div>
                            ) : (
                              <select 
                                className="tt-select" 
                                value="" 
                                onChange={e => handleAddPeriod(day, p, e.target.value)}
                              >
                                <option value="">—</option>
                                {allocs.filter(a => a.batch === selBatch && a.section === selSection).map(a => (
                                  <option key={a.id} value={a.id}>{a.course_code}</option>
                                ))}
                              </select>
                            )}
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
