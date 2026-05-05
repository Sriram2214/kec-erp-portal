import { useEffect, useState } from 'react'
import api from '../../api/index'
import './Reports.css'

export default function Reports() {
  const [reportType, setReportType] = useState('student_detail')
  const [data,       setData]       = useState([])
  const [loading,    setLoading]    = useState(false)
  const [master,     setMaster]     = useState({ departments: [], batches: [] })
  const [allocs,     setAllocs]     = useState([])
  
  const [filters, setFilters] = useState({ batch: '', dept: '', allocation_id: '' })

  useEffect(() => {
    api.get('/master').then(r => {
      setMaster(r.data)
      if (r.data.batches.length > 0) setFilters(f => ({ ...f, batch: r.data.batches[0].label }))
      if (r.data.departments.length > 0) setFilters(f => ({ ...f, dept: r.data.departments[0].code }))
    })
    api.get('/allocations').then(r => setAllocs(r.data))
  }, [])

  const generateReport = async () => {
    setLoading(true); setData([])
    try {
      let url = ''
      if (reportType === 'student_detail') url = `/reports/students?batch=${filters.batch}&dept=${filters.dept}`
      if (reportType === 'marks_analysis') url = `/reports/marks-analysis?allocation_id=${filters.allocation_id}`
      if (reportType === 'attendance')     url = `/reports/attendance-summary?batch=${filters.batch}&dept=${filters.dept}`
      
      const res = await api.get(url)
      setData(res.data.details || res.data)
    } catch {}
    finally { setLoading(false) }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Reports</div>
        <div className="page-title">Reporting Engine</div>
        <div className="page-sub">Institutional Analytics & Data Exports (Phase 5)</div>
      </div>

      <div className="card report-config">
        <div className="report-config-grid">
          <div className="field">
            <label>Report Type</label>
            <select value={reportType} onChange={e => setReportType(e.target.value)}>
              <option value="student_detail">18. Student Detail Report</option>
              <option value="marks_analysis">19. Internal Mark Analysis</option>
              <option value="attendance">20. Attendance Status Report</option>
              <option value="result_galley">31. Result Galley (Master Sheet)</option>
              <option value="faculty_performance">34. Faculty-wise Report</option>
              <option value="class_grades">32. Class-wise Grades Report</option>
            </select>
          </div>

          {reportType === 'marks_analysis' ? (
            <div className="field">
              <label>Select Course / Allocation</label>
              <select value={filters.allocation_id} onChange={e => setFilters({...filters, allocation_id: e.target.value})}>
                <option value="">— Select —</option>
                {allocs.map(a => <option key={a.id} value={a.id}>{a.course_code} ({a.batch})</option>)}
              </select>
            </div>
          ) : (
            <>
              <div className="field">
                <label>Batch</label>
                <select value={filters.batch} onChange={e => setFilters({...filters, batch: e.target.value})}>
                  {master.batches.map(b => <option key={b.id} value={b.label}>{b.label}</option>)}
                </select>
              </div>
              <div className="field">
                <label>Department</label>
                <select value={filters.dept} onChange={e => setFilters({...filters, dept: e.target.value})}>
                  {master.departments.map(d => <option key={d.id} value={d.code}>{d.code}</option>)}
                </select>
              </div>
            </>
          )}

          <div className="field" style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button className="btn btn-gold w-100" onClick={generateReport} disabled={loading}>
              {loading ? 'Generating...' : 'Generate Report'}
            </button>
          </div>
        </div>
      </div>

      {data.length > 0 && (
        <div className="card report-results fade-in">
          <div className="report-header-actions">
            <div className="card-title">Report Data</div>
            <button className="btn btn-sm btn-outline" onClick={() => window.print()}>Print / Export PDF</button>
          </div>
          
          <table className="ese-table">
            <thead>
              {reportType === 'student_detail' && (
                <tr><th>Reg. Number</th><th>Name</th><th>Dept</th><th>Email</th></tr>
              )}
              {reportType === 'marks_analysis' && (
                <tr><th>Reg. Number</th><th>Name</th><th>Marks (50)</th><th>Assign (10)</th></tr>
              )}
              {reportType === 'attendance' && (
                <tr><th>Reg. Number</th><th>Name</th><th>Total Hrs</th><th>Attended</th><th>%</th></tr>
              )}
              {reportType === 'result_galley' && data.courses && (
                <tr>
                  <th>Register Number</th>
                  <th>Student Name</th>
                  {data.courses.map(c => <th key={c}>{c}</th>)}
                </tr>
              )}
              {reportType === 'faculty_performance' && (
                <tr><th>Course Name</th><th>Batch</th><th>Students</th><th>Passed</th><th>Pass %</th></tr>
              )}
            </thead>
            <tbody>
              {(data.data || data).map((item, i) => (
                <tr key={i}>
                  {reportType === 'faculty_performance' ? (
                    <>
                      <td><strong>{item.course}</strong></td>
                      <td className="mono">{item.batch}</td>
                      <td>{item.total}</td>
                      <td>{item.passed}</td>
                      <td>
                        <span className={`badge ${item.pass_percentage >= 90 ? 'badge-green' : 'badge-gold'}`}>
                          {item.pass_percentage.toFixed(1)}%
                        </span>
                      </td>
                    </>
                  ) : (
                    <>
                      {reportType === 'result_galley' ? (
                        <>
                          <td className="mono">{item.regno}</td>
                          <td><strong>{item.name}</strong></td>
                          {data.courses.map(c => (
                            <td key={c} align="center">
                              <span className={`badge ${item.grades[c] === 'U' ? 'badge-red' : item.grades[c] !== '-' ? 'badge-green' : ''}`}>
                                {item.grades[c]}
                              </span>
                            </td>
                          ))}
                        </>
                      ) : (
                        <>
                          {reportType === 'student_detail' && (
                            <>
                              <td className="mono">{item.regno}</td>
                              <td><strong>{item.name}</strong></td>
                              <td>{item.dept}</td>
                              <td className="muted">{item.email}</td>
                            </>
                          )}
                          {reportType === 'marks_analysis' && (
                            <>
                              <td className="mono">{item.regno}</td>
                              <td><strong>{item.name}</strong></td>
                              <td>{item.marks}</td>
                              <td>{item.assignment}</td>
                            </>
                          )}
                          {reportType === 'attendance' && (
                            <>
                              <td className="mono">{item.regno}</td>
                              <td><strong>{item.name}</strong></td>
                              <td>{item.total_hours}</td>
                              <td>{item.attended_hours}</td>
                              <td>
                                <span className={`badge ${item.percentage < 75 ? 'badge-red' : 'badge-green'}`}>
                                  {item.percentage.toFixed(1)}%
                                </span>
                              </td>
                            </>
                          )}
                        </>
                      )}
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
