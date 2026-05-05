import './Splash.css'

export default function Splash({ isVisible = true }) {
  return (
    <div className={`splash-screen ${!isVisible ? 'fade-out' : ''}`}>
      <div className="splash-bg"></div>
      <div className="splash-overlay"></div>
      
      <div className="splash-content">
        <div className="splash-logo">
          <img src="/logo.png" alt="KEC Logo" />
        </div>
        
        <div className="splash-text-wrap">
          <h1 className="splash-text">
            KINGS ENGINEERING
            <span>COLLEGE</span>
          </h1>
        </div>

        <div className="splash-loader">
          <div className="splash-loader-bar"></div>
        </div>
      </div>
    </div>
  )
}
