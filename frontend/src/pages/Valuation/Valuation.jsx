import React from 'react';
import { Construction, Timer, ShieldCheck, Cog } from 'lucide-react';

export default function Valuation() {
  return (
    <div className="fade-in" style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center', 
      minHeight: '70vh',
      textAlign: 'center'
    }}>
      <div className="coming-soon-card" style={{
        background: 'white',
        padding: '3rem',
        borderRadius: '24px',
        boxShadow: '0 20px 50px rgba(0,0,0,0.05)',
        border: '1px solid #eee',
        maxWidth: '600px',
        width: '90%'
      }}>
        <div style={{ 
          width: '80px', 
          height: '80px', 
          background: '#fef3c7', 
          borderRadius: '20px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          margin: '0 auto 2rem',
          color: '#d4af37'
        }}>
          <Construction size={40} />
        </div>

        <h1 style={{ 
          fontFamily: 'Cinzel, serif', 
          fontSize: '2rem', 
          color: '#1a1a1a', 
          marginBottom: '1rem',
          fontWeight: 800
        }}>
          Valuation Engine
        </h1>
        
        <div style={{ 
          display: 'inline-flex', 
          alignItems: 'center', 
          gap: '8px', 
          padding: '6px 16px', 
          background: '#1a1a1a', 
          color: '#d4af37', 
          borderRadius: '99px',
          fontSize: '0.75rem',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          marginBottom: '1.5rem'
        }}>
          <Timer size={14} />
          Coming Soon
        </div>

        <p style={{ 
          color: '#64748b', 
          lineHeight: '1.6', 
          fontSize: '1rem',
          marginBottom: '2.5rem'
        }}>
          The advanced **Digital Valuation & Grade Processing Center** is currently undergoing security hardening. 
          This module will feature automated Foil mapping and Dummy Number synchronization for the upcoming semester.
        </p>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: '1fr 1fr', 
          gap: '1rem',
          borderTop: '1px solid #eee',
          paddingTop: '2rem'
        }}>
          <div style={{ textAlign: 'left', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ color: '#d4af37' }}><ShieldCheck size={20} /></div>
            <div style={{ fontSize: '0.8rem', color: '#444', fontWeight: 600 }}>Elite Security Layer</div>
          </div>
          <div style={{ textAlign: 'left', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ color: '#d4af37' }}><Cog size={20} /></div>
            <div style={{ fontSize: '0.8rem', color: '#444', fontWeight: 600 }}>Automated Grading</div>
          </div>
        </div>
      </div>
    </div>
  );
}
