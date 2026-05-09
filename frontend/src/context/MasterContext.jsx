import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api/index'

const MasterContext = createContext(null)

export function MasterProvider({ children }) {
  const [master, setMaster] = useState({
    departments: [],
    batches: [],
    regulations: [],
    degrees: [],
    academic_years: [],
    courses: []
  })
  const [loading, setLoading] = useState(true)

  const refreshMaster = async (force = false) => {
    if (!force) {
      const cached = localStorage.getItem('kec_master_data')
      if (cached) {
        const { data, timestamp } = JSON.parse(cached)
        // Cache for 1 hour
        if (Date.now() - timestamp < 3600000) {
          setMaster(data)
          setLoading(false)
          return data
        }
      }
    }

    try {
      // 1. Fetch Master Data (Fast)
      const masterRes = await api.get('/master')
      setMaster(prev => ({ ...prev, ...masterRes.data }))
      setLoading(false) // Allow UI to render with master data

      // 2. Fetch Courses (Heavier) in the background
      const coursesRes = await api.get('/courses?fields=minimal_meta')
      // Group Batches
      const batches = masterRes.data.batches || [];
      const sortedBatches = [...batches].sort((a, b) => b.label.localeCompare(a.label));
      const groupedBatches = { ug: [], pg: [], phd: [], other: [] };
      
      sortedBatches.forEach(b => {
        const parts = b.label.split('-');
        if (parts.length === 2) {
          const duration = parseInt(parts[1]) - parseInt(parts[0]);
          if (duration === 4) groupedBatches.ug.push(b);
          else if (duration === 2) groupedBatches.pg.push(b);
          else if (duration >= 5) groupedBatches.phd.push(b);
          else groupedBatches.other.push(b);
        } else {
          groupedBatches.other.push(b);
        }
      });

      const newData = {
        ...masterRes.data,
        groupedBatches,
        courses: coursesRes.data
      }
      
      setMaster(newData)
      localStorage.setItem('kec_master_data', JSON.stringify({
        data: newData,
        timestamp: Date.now()
      }))
      return newData
    } catch (e) {
      console.error('Failed to fetch master data', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refreshMaster()
  }, [])

  return (
    <MasterContext.Provider value={{ master, loading, refreshMaster }}>
      {children}
    </MasterContext.Provider>
  )
}

export const useMaster = () => useContext(MasterContext)
