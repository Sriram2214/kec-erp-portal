import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#f8fafc',
          textAlign: 'center',
          padding: '2rem'
        }}>
          <div style={{ 
            fontSize: '3rem', 
            marginBottom: '1rem' 
          }}>⚠️</div>
          <h1 style={{ 
            fontFamily: 'Cinzel, serif', 
            color: '#1a1a1a',
            fontSize: '1.5rem',
            marginBottom: '1rem'
          }}>
            Institutional Logic Error
          </h1>
          <p style={{ color: '#64748b', maxWidth: '400px', marginBottom: '2rem' }}>
            The system encountered an unexpected rendering error. Please try refreshing the portal or contact the COE technical cell.
          </p>
          <button 
            onClick={() => window.location.reload()}
            style={{
              padding: '0.8rem 2rem',
              background: '#1a1a1a',
              color: '#d4af37',
              border: 'none',
              borderRadius: '8px',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Refresh Portal
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
