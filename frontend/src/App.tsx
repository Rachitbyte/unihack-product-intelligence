import { useState } from 'react';
import './App.css';

interface JobResponse {
  id: string;
  status: string;
  total_rows: int;
  processed_rows: int;
  failed_rows: int;
  created_at: string;
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [job, setJob] = useState<JobResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      // 1. Create Job
      const createRes = await fetch(`${API_BASE}/api/jobs`, { method: 'POST' });
      if (!createRes.ok) throw new Error("Failed to create job");
      const jobData = await createRes.json();

      // 2. Upload File
      const formData = new FormData();
      formData.append('file', file);
      
      const uploadRes = await fetch(`${API_BASE}/api/jobs/${jobData.id}/upload`, {
        method: 'POST',
        body: formData
      });
      if (!uploadRes.ok) throw new Error("Failed to upload file");
      const uploadedJob = await uploadRes.json();
      setJob(uploadedJob);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (job) window.open(`${API_BASE}/api/jobs/${job.id}/download/csv`, '_blank');
  };

  const downloadXLSX = () => {
    if (job) window.open(`${API_BASE}/api/jobs/${job.id}/download/xlsx`, '_blank');
  };

  return (
    <div className="container">
      <header>
        <h1>UniHack Product Intelligence (UPIE)</h1>
      </header>
      <main>
        <section className="upload-section">
          <h2>1. Upload Input CSV</h2>
          <input 
            type="file" 
            accept=".csv" 
            onChange={(e) => setFile(e.target.files?.[0] || null)} 
          />
          <button onClick={handleUpload} disabled={loading || !file}>
            {loading ? "Processing..." : "Process Data"}
          </button>
          {error && <p className="error">{error}</p>}
        </section>

        {job && (
          <section className="results-section">
            <h2>2. Results</h2>
            <div className="status-card">
              <p><strong>Job ID:</strong> {job.id}</p>
              <p><strong>Status:</strong> {job.status}</p>
              <p><strong>Total Rows:</strong> {job.total_rows}</p>
              <p><strong>Processed:</strong> {job.processed_rows}</p>
              <p><strong>Failed:</strong> {job.failed_rows}</p>
            </div>
            
            <div className="actions">
              <h2>3. Download Enriched Schema</h2>
              <button onClick={downloadCSV}>Download CSV</button>
              <button onClick={downloadXLSX}>Download XLSX</button>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
