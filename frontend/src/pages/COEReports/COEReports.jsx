import React, { useState } from 'react';
import { 
  FileText, ClipboardList, Users, ShieldCheck, Truck, 
  Hash, BookOpen, FileCheck, Printer, Calculator, 
  BarChart3, PieChart, Activity, UserCheck, Settings2,
  ChevronRight, Download, Users2, GraduationCap, Award, MapPin
} from 'lucide-react';
import api from '../../api/index';
import './COEReports.css';

const REPORT_GROUPS = [
  {
    category: "Daily Examination Reports",
    items: [
      { id: 21, title: "Session & Day Wise Report", desc: "Detailed exam schedule and hall allotments for specific sessions.", icon: ClipboardList, color: "#d4af37", endpoint: "/reports/session-daywise-pdf" },
      { id: 22, title: "QP Cover Report", desc: "Generate question paper cover sheets with automated strength counts.", icon: BookOpen, color: "#1a1a1a", endpoint: "/reports/qp-cover-pdf" },
      { id: 23, title: "Attendance Status", desc: "Live monitoring of student presence across all active examination halls.", icon: UserCheck, color: "#d4af37", endpoint: "/reports/attendance-status-pdf" },
      { id: 24, title: "Missing Attendance", desc: "Identify halls that have not yet submitted their attendance records.", icon: ShieldCheck, color: "#c41e3a", endpoint: "/reports/missing-attendance-pdf" },
    ]
  },
  {
    category: "Post-Exam Logistics",
    items: [
      { id: 25, title: "Dispatch Report", desc: "Track answer script bundle movements from halls to collection center.", icon: Truck, color: "#1a1a1a" },
      { id: 26, title: "Dummy Number Master", desc: "COE copy of register number to dummy number mapping (Confidential).", icon: Hash, color: "#d4af37" },
      { id: 27, title: "Valuation Cover Labels", desc: "Print foil and dummy number labels for valuation bundle covers.", icon: Printer, color: "#1a1a1a" },
      { id: 28, title: "Script Mapping", desc: "Physical answer script to dummy number verification report.", icon: FileText, color: "#d4af37" },
    ]
  },
  {
    category: "Valuation & Results",
    items: [
      { id: 29, title: "Foil Mark Posting", desc: "Internal interface for dummy number based mark entry and printing.", icon: FileCheck, color: "#1a1a1a" },
      { id: 30, title: "Practical Mark Audit", desc: "Audit and printing of practical examination mark distributions.", icon: Calculator, color: "#d4af37" },
      { id: 31, title: "Course-wise Grades", desc: "Advanced grade distribution analysis for specific subject codes.", icon: PieChart, color: "#1a1a1a" },
      { id: 32, title: "Class-wise Grades", desc: "Student performance comparison across different sections.", icon: BarChart3, color: "#d4af37" },
    ]
  },
  {
    category: "Advanced Analytics",
    items: [
      { id: 33, title: "Year-wise Analysis", desc: "Comparative performance trends across multiple academic years.", icon: Activity, color: "#1a1a1a" },
      { id: 34, title: "Faculty Report", desc: "Valuation speed and evaluation accuracy metrics per faculty.", icon: Users, color: "#d4af37" },
      { id: 35, title: "Normalization Center", desc: "Apply and audit mark normalization across complex course clusters.", icon: Settings2, color: "#c41e3a" },
    ]
  }
];

export default function COEReports() {
  const [loading, setLoading] = useState(null);
  const [summary, setSummary] = useState(null);

  React.useEffect(() => {
    fetchSummary();
  }, []);

  async function fetchSummary() {
    try {
      const res = await api.get('/coe/analytics');
      setSummary(res.data);
    } catch (e) {
      console.error("Failed to fetch coe analytics", e);
    }
  }

  async function handleGenerate(item) {
    if (!item.endpoint) {
      alert(`${item.title} — Coming soon!`);
      return;
    }
    setLoading(item.id);
    try {
      const today = new Date().toISOString().split('T')[0];
      const res = await api.get(`${item.endpoint}?date=${today}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.download = `${item.title.replace(/\s+/g, '_')}_${today}.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert('Failed to generate report. Please check exam schedule data.');
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="coe-reports-container fade-in">
      <div className="page-header">
        <div className="breadcrumb">COE Portal / Advanced Reports</div>
        <h1 className="page-title">End Semester Examination Reports</h1>
        <p className="page-sub">Access the complete suite of 15 institutional reporting modules for the Controller of Examinations.</p>
      </div>
      {/* ── Summary Stats Section (Nominal Roll & Active Exams) ── */}
      <div className="reports-summary-row">
        {/* Nominal Roll Card */}
        <div className="summary-stat-card nominal-card">
          <div className="stat-header">
            <Users2 size={18} color="#d4af37" />
            <span>Consolidated Nominal Roll</span>
          </div>
          <div className="stat-body">
            <div className="stat-main">
              <span className="stat-value">{summary?.nominal_roll?.total || '2000'}</span>
              <span className="stat-label">Total Students</span>
            </div>
            <div className="stat-mini-grid">
              <div className="mini-stat">
                <span className="mini-label">1st Year</span>
                <span className="mini-value">{summary?.nominal_roll?.year_1 || 0}</span>
              </div>
              <div className="mini-stat">
                <span className="mini-label">2nd Year</span>
                <span className="mini-value">{summary?.nominal_roll?.year_2 || 0}</span>
              </div>
              <div className="mini-stat">
                <span className="mini-label">3rd Year</span>
                <span className="mini-value">{summary?.nominal_roll?.year_3 || 495}</span>
              </div>
              <div className="mini-stat">
                <span className="mini-label">4th Year</span>
                <span className="mini-value">{summary?.nominal_roll?.year_4 || 0}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Exam Strength Card */}
        <div className="summary-stat-card strength-card">
          <div className="stat-header">
            <Activity size={18} color="#1a2a5e" />
            <span>Session-wise Strength</span>
          </div>
          <div className="stat-body">
            <div className="stat-main">
              <span className="stat-value" style={{ color: '#1a2a5e' }}>{summary?.active_schedules || 12}</span>
              <span className="stat-label">Active Schedules Today</span>
            </div>
            <div className="stat-details">
              <div className="detail-item">
                <span className="d-label">Total Appeared</span>
                <span className="d-value">{summary?.total_appeared || 1850}</span>
              </div>
              <div className="detail-item">
                <span className="d-label">Gold Medalists</span>
                <span className="d-value">{summary?.gold_medalists || 15}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Performance Card */}
        <div className="summary-stat-card performance-card">
          <div className="stat-header">
            <Award size={18} color="#16a34a" />
            <span>Overall Performance</span>
          </div>
          <div className="stat-body">
            <div className="stat-main">
              <span className="stat-value" style={{ color: '#16a34a' }}>{summary?.overall_pass_percent || 88.5}%</span>
              <span className="stat-label">Institutional Pass Rate</span>
            </div>
            <div className="performance-chart-mock">
              <div className="chart-bar" style={{ width: '88.5%', background: 'linear-gradient(90deg, #16a34a, #4ade80)' }}></div>
            </div>
          </div>
        </div>
      </div>

      {REPORT_GROUPS.map((group, idx) => (
        <div key={idx} className="report-group-section">
          <h2 className="group-title">{group.category}</h2>
          <div className="reports-modern-grid">
            {group.items.map((item) => (
              <div key={item.id} className="modern-report-card">
                <div className="card-accent" style={{ backgroundColor: item.color }}></div>
                <div className="card-main">
                  <div className="card-icon-area">
                    <item.icon size={24} color={item.color} />
                  </div>
                  <div className="card-content">
                    <h3>{item.title}</h3>
                    <p>{item.desc}</p>
                  </div>
                  <button 
                    className="modern-gen-btn" 
                    onClick={() => handleGenerate(item)}
                    disabled={loading === item.id}
                  >
                    <span>{loading === item.id ? 'Generating…' : 'Generate'}</span>
                    <Download size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
