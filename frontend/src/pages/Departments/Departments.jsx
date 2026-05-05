import { useEffect, useState } from 'react'
import api from '../../api/index'
import { Building2, Plus, Trash2, Edit } from 'lucide-react'
import './Departments.css'

export default function Departments() {
  const [depts, setDepts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [newDept, setNewDept] = useState({ code: '', name: '', degree_id: 1 })

  const load = () => {
    setLoading(true)
    api.get('/master')
      .then(r => setDepts(r.data.departments || []))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleAdd = async (e) => {
    e.preventDefault()
    try {
      await api.post('/master/departments', newDept)
      setNewDept({ code: '', name: '', degree_id: 1 })
      setShowAdd(false)
      load()
    } catch { alert('Failed to add department') }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this department?')) return
    try {
      await api.delete(`/master/departments/${id}`)
      load()
    } catch { alert('Failed to delete') }
  }

  return (
    <div className="fade-in departments-page">
      <div className="page-header">
        <div className="breadcrumb">KCE ERP › Configuration</div>
        <div className="page-title">Department Registry</div>
        <div className="page-sub">Institutional department master list and academic codes</div>
      </div>

      <div className="actions-bar">
        <button className="btn btn-gold" onClick={() => setShowAdd(!showAdd)}>
          <Plus size={18} /> {showAdd ? 'Close' : 'Add Department'}
        </button>
      </div>

      {showAdd && (
        <div className="card form-card fade-in">
          <form onSubmit={handleAdd} className="form-grid">
            <div className="field">
              <label>Code (e.g. AI&DS)</label>
              <input required value={newDept.code} onChange={e => setNewDept({...newDept, code: e.target.value.toUpperCase()})} />
            </div>
            <div className="field">
              <label>Full Name</label>
              <input required value={newDept.name} onChange={e => setNewDept({...newDept, name: e.target.value})} />
            </div>
            <div className="field">
              <label>Degree ID</label>
              <input type="number" value={newDept.degree_id} onChange={e => setNewDept({...newDept, degree_id: e.target.value})} />
            </div>
            <button type="submit" className="btn btn-gold" style={{ marginTop: '22px' }}>Save Department</button>
          </form>
        </div>
      )}

      {loading ? <div className="loading-row">Loading Departments...</div> : (
        <div className="depts-grid">
          {depts.map(d => (
            <div key={d.id} className="card dept-card">
              <div className="dept-icon-box">
                <Building2 size={24} color="var(--gold-vivid)" />
              </div>
              <div className="dept-info">
                <div className="dept-code">{d.code}</div>
                <div className="dept-full-name">{d.name}</div>
              </div>
              <div className="dept-actions">
                <button className="icon-btn red" onClick={() => handleDelete(d.id)}><Trash2 size={16} /></button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
