import React from 'react';
import { StatusBadge } from './ResultsTable';

interface EvidenceProps {
  attribute: string;
  evidence_text: string;
  source_url: string;
  source_type: string;
  validation_status: string;
  confidence: number;
  onClose: () => void;
}

const SourceEvidenceModal: React.FC<EvidenceProps> = ({
  attribute,
  evidence_text,
  source_url,
  source_type,
  validation_status,
  confidence,
  onClose
}) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3 style={{ margin: 0 }}>Evidence: {attribute}</h3>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <div className="stat-label">Source URL</div>
              <a href={source_url} target="_blank" rel="noreferrer" style={{ color: '#3b82f6', wordBreak: 'break-all' }}>
                {source_url}
              </a>
            </div>
            <div>
              <div className="stat-label">Source Type</div>
              <div>{source_type || "Manufacturer Webpage"}</div>
            </div>
            <div>
              <div className="stat-label">Validation Status</div>
              <StatusBadge status={validation_status} />
            </div>
            <div>
              <div className="stat-label">Operational Confidence</div>
              <div>{(confidence * 100).toFixed(0)}%</div>
            </div>
          </div>
        </div>
        <div className="modal-body">
          {evidence_text || "No specific evidence text extracted."}
        </div>
      </div>
    </div>
  );
};

export default SourceEvidenceModal;
