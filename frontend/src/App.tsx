import { useState } from 'react';
import './App.css';
import JobProgress from './components/JobProgress';
import ResultsTable from './components/ResultsTable';
import type { ProductRow } from './components/ResultsTable';
import ProductDetailsDrawer from './components/ProductDetailsDrawer';

interface JobResponse {
  id: string;
  status: string;
  total_rows: number;
  processed_rows: number;
  failed_rows: number;
  created_at: string;
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [job, setJob] = useState<JobResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rows, setRows] = useState<ProductRow[]>([]);
  const [selectedRow, setSelectedRow] = useState<ProductRow | null>(null);

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchJobResults = async (jobId: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/jobs/${jobId}/results`);
      if (res.ok) {
        const data = await res.json();
        setRows(data.rows || []);
      }
    } catch (err) {
      console.error("Failed to fetch job results", err);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file.");
      return;
    }
    setLoading(true);
    setError(null);
    setRows([]);
    setJob(null);
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
      
      // Fetch results for the table
      await fetchJobResults(uploadedJob.id);
      
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
        <h1>UniHack Product Intelligence</h1>
        <p style={{ color: 'var(--text-secondary)' }}>AI-Powered E-Commerce Data Enrichment</p>
      </header>
      
      <main style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        <section className="panel upload-section" style={{ marginBottom: 0 }}>
          <div style={{ flex: 1 }}>
            <h2 style={{ margin: 0 }}>Upload CSV</h2>
            <p className="stat-label">Upload a list of Manufacturer Part Numbers (MPNs) to begin.</p>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <input 
              type="file" 
              accept=".csv" 
              onChange={(e) => setFile(e.target.files?.[0] || null)} 
            />
            <button onClick={handleUpload} disabled={loading || !file}>
              {loading ? "Processing..." : "Process Data"}
            </button>
          </div>
        </section>

        {error && <div className="panel" style={{ color: 'var(--status-conflict)' }}>{error}</div>}

        {job && (
          <>
            <JobProgress job={job} />
            
            <div className="panel" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 0 }}>
              <h3 style={{ margin: 0 }}>Export Data</h3>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button className="secondary" onClick={downloadCSV}>Download 252-Col CSV</button>
                <button className="secondary" onClick={downloadXLSX}>Download 252-Col XLSX</button>
              </div>
            </div>

            <ResultsTable rows={rows} onRowClick={setSelectedRow} />
          </>
        )}
      </main>

      {selectedRow && (
        <ProductDetailsDrawer 
          row={selectedRow} 
          onClose={() => setSelectedRow(null)} 
        />
      )}
    </div>
  );
}

export default App;
