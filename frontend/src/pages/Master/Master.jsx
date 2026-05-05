import { useEffect, useState } from 'react'
import api from '../../api/index'
import './Master.css'

export default function Master() {
  const [activeTab, setActiveTab] = useState('dept')
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ name: '', code: '', label: '', semester: 'Odd', is_current: false })
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')

  const endpoints = {
    dept: '/master/departments',
    degree: '/master/degrees',
    batch: '/master/batches',
    reg: '/master/regulations',
    ay: '/master/academic-years'
  }

  const load = () => {
    setLoading(true)
    api.get(endpoints[activeTab])
      .then(r => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
    setForm({ name: '', code: '', label: '', semester: 'Odd', is_current: false })
    setErr('')
  }, [activeTab])

  const handleAdd = async (e) => {
    e.preventDefault()
    setSaving(true); setErr('')
    try {
      await api.post(endpoints[activeTab], form)
      load()
      setForm({ name: '', code: '', label: '', semester: 'Odd', is_current: false })
    } catch (ex) {
      setErr(ex.response?.data?.message || 'Failed to add item')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="breadcrumb">KEC ERP › Academic Master</div>
        <div className="page-title">Academic Master Data</div>
        <div className="page-sub">Configure Institutional Foundation (Phases 1 & 2)</div>
      </div>

      <div className="master-tabs">
        {[
          { id: 'dept',   label: 'Departments' },
          { id: 'degree', label: 'Degrees' },
          { id: 'batch',  label: 'Batches' },
          { id: 'reg',    label: 'Regulations' },
          { id: 'ay',     label: 'Academic Years' },
        ].map(t => (
          <button 
            key={t.id} 
            className={`master-tab ${activeTab === t.id ? 'active' : ''}`}
            onClick={() => setActiveTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="master-grid">
        {/* Form Card */}
        <div className="card master-form-card">
          <div className="card-title">Add New {activeTab.toUpperCase()}</div>
          <form onSubmit={handleAdd} className="master-form">
            {activeTab === 'dept' && (
              <>
                <div className="field">
                  <label>Department Code (e.g. CSE)</label>
                  <input required value={form.code} onChange={e => setForm({...form, code: e.target.value})} />
                </div>
                <div className="field">
                  <label>Full Name</label>
                  <input required value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
                </div>
              </>
            )}

            {(activeTab === 'degree' || activeTab === 'reg') && (
              <div className="field">
                <label>Name (e.g. BE or R2021)</label>
                <input required value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
              </div>
            )}

            {activeTab === 'batch' && (
              <div className="field">
                <label>Label (e.g. 2021-2025)</label>
                <input required value={form.label} onChange={e => setForm({...form, label: e.target.value})} />
              </div>
            )}

            {activeTab === 'ay' && (
              <>
                <div className="field">
                  <label>Label (e.g. 2024-25)</label>
                  <input required value={form.label} onChange={e => setForm({...form, label: e.target.value})} />
                </div>
                <div className="field">
                  <label>Semester</label>
                  <select value={form.semester} onChange={e => setForm({...form, semester: e.target.value})}>
                    <option>Odd</option>
                    <option>Even</option>
                  </select>
                </div>
                <div className="field-row">
                  <input type="checkbox" id="curr" checked={form.is_current} onChange={e => setForm({...form, is_current: e.target.checked})} />
                  <label htmlFor="curr">Set as Current Active Year</label>
                </div>
              </>
            )}

            {err && <div className="alert-error">{err}</div>}
            <button className="btn btn-gold w-100" disabled={saving}>
              {saving ? 'Saving...' : 'Add Record'}
            </button>
          </form>
        </div>

        {/* List Card */}
        <div className="card master-list-card">
          <div className="card-title">Existing Records</div>
          {loading ? (
            <div className="empty-row">Loading records...</div>
          ) : (
            <table className="master-table">
              <thead>
                <tr>
                  {activeTab === 'dept' && (
                    <>
                      <th>Code</th>
                      <th>Name</th>
                    </>
                  )}
                  {activeTab === 'ay' && (
                    <>
                      <th>Year</th>
                      <th>Sem</th>
                      <th>Status</th>
                    </>
                  )}
                  {(activeTab !== 'dept' && activeTab !== 'ay') && <th>Name / Label</th>}
                </tr>
              </thead>
              <tbody>
                {data.map(item => (
                  <tr key={item.id}>
                    {activeTab === 'dept' && (
                      <>
                        <td className="mono"><strong>{item.code}</strong></td>
                        <td>{item.name}</td>
                      </>
                    )}
                    {activeTab === 'ay' && (
                      <>
                        <td className="mono">{item.label}</td>
                        <td>{item.semester}</td>
                        <td>
                          {item.is_current ? 
                            <span className="badge badge-gold">Active</span> : 
                            <span className="badge badge-blue">Archive</span>
                          }
                        </td>
                      </>
                    )}
                    {(activeTab !== 'dept' && activeTab !== 'ay') && <td>{item.name || item.label}</td>}
                  </tr>
                ))}
                {data.length === 0 && (
                  <tr><td colSpan="3" className="empty-row">No records found.</td></tr>
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}
