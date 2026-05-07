import { useEffect, useState } from 'react'
import api from '../../api/index'
import '../Students/Students.css'

const EMPTY = { course_code: '', course_title: '', department: '', credits: 3, batch: '', semester: 1 }

import { useMaster } from '../../context/MasterContext'

export default function Courses() {
  const [courses, setCourses] = useState([])
  const { master }            = useMaster()
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({ degree_id: '', department_id: '', batch_id: '', regulation_id: '' })
  const [search,  setSearch]  = useState('')

  const loadCourses = () => {
    if (!filters.degree_id || !filters.department_id || !filters.batch_id || !filters.regulation_id) {
        setCourses([])
        return
    }
    setLoading(true)
    api.get('/courses', { params: filters })
       .then(r => setCourses(r.data))
       .finally(() => setLoading(false))
  }

  useEffect(() => { loadCourses() }, [filters])

  const filtered = courses.filter(c => 
    c.course_title.toLowerCase().includes(search.toLowerCase()) ||
    c.course_code.toLowerCase().includes(search.toLowerCase())
  )

  // Group by semester
  const grouped = filtered.reduce((acc, c) => {
    if (!acc[c.semester]) acc[c.semester] = []
    acc[c.semester].push(c)
    return acc
  }, {})

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Academic</div>
        <div className="page-title">Curriculum & Course Mapping</div>
        <div className="page-sub">Manage institutional curriculum structures by Batch and Regulation</div>
      </div>

      <div className="filter-bar card">
        <div className="filter-row">
          <div className="filter-group cascading">
            <select value={filters.degree_id} onChange={e => setFilters({...filters, degree_id: e.target.value, department_id: '', batch_id: '', regulation_id: ''})}>
              <option value="">Select Degree</option>
              {master.degrees.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
            
            <select disabled={!filters.degree_id} value={filters.department_id} onChange={e => setFilters({...filters, department_id: e.target.value})}>
              <option value="">Select Department</option>
              {master.departments.filter(d => d.degree_id == filters.degree_id).map(d => <option key={d.id} value={d.id}>{d.code} - {d.name}</option>)}
            </select>

            <select disabled={!filters.department_id} value={filters.batch_id} onChange={e => setFilters({...filters, batch_id: e.target.value})}>
              <option value="">Select Batch</option>
              {master.batches.map(b => <option key={b.id} value={b.id}>{b.label}</option>)}
            </select>

            <select disabled={!filters.batch_id} value={filters.regulation_id} onChange={e => setFilters({...filters, regulation_id: e.target.value})}>
              <option value="">Select Regulation</option>
              {master.regulations.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
            </select>
          </div>
          <input className="search-input" placeholder="Search title / code…" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
      </div>

      <div className="course-list">
        {loading ? (
            <div className="card loading-state">
                <div className="spinner"></div>
                <p>Fetching Curriculum Data...</p>
            </div>
        ) : Object.keys(grouped).length > 0 ? (
          Object.keys(grouped).sort((a,b) => a-b).map(sem => (
            <div key={sem} className="semester-group card">
              <div className="semester-header">Semester {sem}</div>
              <table>
                <thead>
                  <tr>
                    <th style={{width: '120px'}}>Code</th>
                    <th>Course Title</th>
                    <th style={{width: '80px'}}>Credits</th>
                    <th style={{width: '120px'}}>Regulation</th>
                    <th style={{width: '120px'}}>Type</th>
                  </tr>
                </thead>
                <tbody>
                  {grouped[sem].map(c => (
                    <tr key={c.id}>
                      <td className="mono"><strong>{c.course_code}</strong></td>
                      <td>{c.course_title}</td>
                      <td>{c.credits}</td>
                      <td><span className="badge badge-gold">{c.regulation}</span></td>
                      <td>
                        <span className={`badge ${c.is_lab ? 'badge-blue' : 'badge-outline'}`}>
                          {c.is_lab ? 'Practical' : 'Theory'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))
        ) : (
          <div className="card empty-state">
            <p>{!filters.regulation_id ? 'Please select all filters to view curriculum' : 'No courses found for this combination.'}</p>
          </div>
        )}
      </div>
    </div>
  )
}
