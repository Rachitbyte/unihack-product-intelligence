import React from 'react';

interface JobResponse {
  id: string;
  status: string;
  total_rows: number;
  processed_rows: number;
  failed_rows: number;
}

interface Props {
  job: JobResponse;
}

const JobProgress: React.FC<Props> = ({ job }) => {
  return (
    <div className="panel progress-grid">
      <div className="stat-card">
        <div className="stat-label">Total Rows</div>
        <div className="stat-value">{job.total_rows}</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Processed</div>
        <div className="stat-value" style={{ color: 'var(--status-verified)' }}>
          {job.processed_rows}
        </div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Failed</div>
        <div className="stat-value" style={{ color: job.failed_rows > 0 ? 'var(--status-conflict)' : 'var(--text-secondary)' }}>
          {job.failed_rows}
        </div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Status</div>
        <div className="stat-value" style={{ fontSize: '1.2rem', marginTop: '0.8rem', color: 'var(--text-primary)' }}>
          {job.status}
        </div>
      </div>
    </div>
  );
};

export default JobProgress;
