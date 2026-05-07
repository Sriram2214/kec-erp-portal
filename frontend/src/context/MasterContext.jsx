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
      const [masterRes, coursesRes] = await Promise.all([
        api.get('/master'),
        api.get('/courses')
      ]);
      
      const newData = {
        ...masterRes.data,
        courses: coursesRes.data
      };
      
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
