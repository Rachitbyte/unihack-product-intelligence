import { useState, useEffect } from 'react';
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
  const [healthStatus, setHealthStatus] = useState<string>("Checking API connection...");

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const checkHealth = async () => {
      try {
        console.log(`Checking API health at: ${API_BASE}/health`);
        const res = await fetch(`${API_BASE}/health`);
        if (res.ok) {
          const data = await res.json();
          setHealthStatus(`Connected to backend (${API_BASE}) - Status: ${data.status}`);
        } else {
          setHealthStatus(`Failed to connect to backend (${API_BASE}) - HTTP ${res.status}`);
        }
      } catch (err: any) {
        setHealthStatus(`Error connecting to backend (${API_BASE}): ${err.message}`);
      }
    };
    checkHealth();
  }, []);

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
      let currentJob = await uploadRes.json();
      setJob(currentJob);
      
      // Poll for job completion
      while (currentJob.status === "CREATED" || currentJob.status === "PROCESSING") {
        await new Promise(resolve => setTimeout(resolve, 2000));
        const pollRes = await fetch(`${API_BASE}/api/jobs/${currentJob.id}`);
        if (!pollRes.ok) break;
        currentJob = await pollRes.json();
        setJob(currentJob);
        // Also fetch partial results to see live progress
        await fetchJobResults(currentJob.id);
      }
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = async (url: string, filename: string) => {
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Download failed: ${res.statusText}`);
      const blob = await res.blob();
      const urlBlob = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = urlBlob;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(urlBlob);
    } catch (err: any) {
      setError(`Download Error: ${err.message}`);
    }
  };

  const downloadCSV = () => {
    if (job) downloadFile(`${API_BASE}/api/jobs/${job.id}/download/csv`, `job_${job.id}_output.csv`);
  };

  const downloadXLSX = () => {
    if (job) downloadFile(`${API_BASE}/api/jobs/${job.id}/download/xlsx`, `job_${job.id}_output.xlsx`);
  };

  return (
    <div className="container">
      <header>
        <h1>UniHack Product Intelligence</h1>
        <p style={{ color: 'var(--text-secondary)' }}>AI-Powered E-Commerce Data Enrichment</p>
        <div style={{ fontSize: '0.85rem', marginTop: '0.5rem', color: healthStatus.includes('Connected') ? 'var(--status-official)' : 'var(--status-conflict)' }}>
          {healthStatus}
        </div>
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
