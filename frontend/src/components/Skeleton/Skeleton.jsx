import './Skeleton.css'

export function Skeleton({ width, height, circle, className = '' }) {
  const style = {
    width: width || '100%',
    height: height || '20px',
    borderRadius: circle ? '50%' : '8px'
  }
  
  return <div className={`skeleton-box ${className}`} style={style} />
}

export function TableSkeleton({ rows = 5, cols = 5 }) {
  return (
    <div className="skeleton-table-wrap">
      {[...Array(rows)].map((_, i) => (
        <div key={i} className="skeleton-row">
          {[...Array(cols)].map((_, j) => (
            <Skeleton key={j} width={j === 0 ? '40px' : '15%'} height="24px" />
          ))}
        </div>
      ))}
    </div>
  )
}
