import React from 'react';
import { useMaster } from '../../context/MasterContext';

export default function BatchOptgroups({ valueKey = 'label' }) {
  const { master } = useMaster();
  
  if (!master || !master.batches) return null;

  const sortedBatches = [...master.batches].sort((a, b) => b.label.localeCompare(a.label));

  const ugBatches = [];
  const pgBatches = [];
  const phdBatches = [];
  const otherBatches = [];

  sortedBatches.forEach(b => {
    const parts = b.label.split('-');
    if (parts.length === 2) {
      const duration = parseInt(parts[1]) - parseInt(parts[0]);
      if (duration === 4) ugBatches.push(b);
      else if (duration === 2) pgBatches.push(b);
      else if (duration >= 5) phdBatches.push(b);
      else otherBatches.push(b);
    } else {
      otherBatches.push(b);
    }
  });

  // Adding inline styles for subtle section styling
  const optgroupStyle = { color: '#64748b', fontWeight: '600', fontStyle: 'normal' };
  const optionStyle = { color: '#1e293b', fontWeight: 'normal' };

  return (
    <>
      {ugBatches.length > 0 && (
        <optgroup label="UG Batches (4 Years)" style={optgroupStyle}>
          {ugBatches.map(b => (
            <option key={b.id} value={valueKey === 'id' ? b.id : b.label} style={optionStyle}>
              {b.label}
            </option>
          ))}
        </optgroup>
      )}
      {pgBatches.length > 0 && (
        <optgroup label="PG Batches (2 Years)" style={optgroupStyle}>
          {pgBatches.map(b => (
            <option key={b.id} value={valueKey === 'id' ? b.id : b.label} style={optionStyle}>
              {b.label}
            </option>
          ))}
        </optgroup>
      )}
      {phdBatches.length > 0 && (
        <optgroup label="PhD / Research" style={optgroupStyle}>
          {phdBatches.map(b => (
            <option key={b.id} value={valueKey === 'id' ? b.id : b.label} style={optionStyle}>
              {b.label}
            </option>
          ))}
        </optgroup>
      )}
      {otherBatches.length > 0 && (
        <optgroup label="Other Batches" style={optgroupStyle}>
          {otherBatches.map(b => (
            <option key={b.id} value={valueKey === 'id' ? b.id : b.label} style={optionStyle}>
              {b.label}
            </option>
          ))}
        </optgroup>
      )}
    </>
  );
}
