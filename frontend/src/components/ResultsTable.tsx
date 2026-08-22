import React, { useState } from 'react';

export interface ProductRow {
  row_id: number;
  mfg_part_num: string;
  part_manuf: string;
  is_valid: boolean;
  identity?: {
    status: string;
    confidence: number;
    candidate_manufacturer: string;
    candidate_brand: string;
    official_source_url: string;
    mpn: string;
    candidate_classpath: string;
  };
  extraction?: {
    status: string;
    facts: any[];
  };
  content?: {
    short_description: string;
    marketing_description: string;
    item_features: string[];
  };
  asset_result?: {
    assets: any[];
  };
}

interface Props {
  rows: ProductRow[];
  onRowClick: (row: ProductRow) => void;
}

const PAGE_SIZE = 25;

const StatusBadge = ({ status }: { status?: string }) => {
  if (!status) return null;
  const lower = status.toLowerCase();
  let className = "badge";
  if (lower === "verified") className += " verified";
  else if (lower === "needs_review") className += " needs_review";
  else if (lower === "conflict" || lower === "rejected_non_official") className += " conflict";
  else if (lower === "failed" || lower === "not_found") className += " failed";
  else className += " failed";

  return <span className={className}>{status.replace(/_/g, ' ')}</span>;
};

const ResultsTable: React.FC<Props> = ({ rows, onRowClick }) => {
  const [page, setPage] = useState(1);
  const totalPages = Math.ceil(rows.length / PAGE_SIZE) || 1;

  const currentRows = rows.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="panel">
      <h3>Processed Products</h3>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>MPN</th>
              <th>Manufacturer</th>
              <th>Brand</th>
              <th>Identity Status</th>
              <th>Confidence</th>
              <th>Extraction Status</th>
            </tr>
          </thead>
          <tbody>
            {currentRows.map((row) => (
              <tr key={row.row_id} onClick={() => onRowClick(row)}>
                <td>{row.mfg_part_num}</td>
                <td>{row.identity?.candidate_manufacturer || row.part_manuf}</td>
                <td>{row.identity?.candidate_brand || "-"}</td>
                <td><StatusBadge status={row.identity?.status || (row.is_valid ? "VALID" : "FAILED")} /></td>
                <td>{row.identity?.confidence ? (row.identity.confidence * 100).toFixed(0) + '%' : "-"}</td>
                <td><StatusBadge status={row.extraction?.status || "PENDING"} /></td>
              </tr>
            ))}
            {currentRows.length === 0 && (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '2rem' }}>No rows found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <span className="stat-label">Showing {(page - 1) * PAGE_SIZE + 1} to {Math.min(page * PAGE_SIZE, rows.length)} of {rows.length} rows</span>
          <div className="page-controls">
            <button 
              className="secondary btn-small" 
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Prev
            </button>
            <span className="stat-label">Page {page} of {totalPages}</span>
            <button 
              className="secondary btn-small" 
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsTable;
export { StatusBadge };
