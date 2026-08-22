import React, { useState } from 'react';
import { StatusBadge } from './ResultsTable';
import type { ProductRow } from './ResultsTable';
import SourceEvidenceModal from './SourceEvidenceModal';

interface Props {
  row: ProductRow;
  onClose: () => void;
}

const ProductDetailsDrawer: React.FC<Props> = ({ row, onClose }) => {
  const [selectedFact, setSelectedFact] = useState<any | null>(null);

  const facts = row.extraction?.facts || [];
  const assets = row.asset_result?.assets || [];
  const content = row.content;

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div className="drawer" onClick={e => e.stopPropagation()}>
        <div className="drawer-header">
          <h2 style={{ margin: 0 }}>Product Details: {row.mfg_part_num}</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>

        <div className="drawer-content">
          {/* Identity Section */}
          <section className="details-section">
            <h3>Identity Resolution</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div><span className="stat-label">MPN:</span> <strong>{row.identity?.mpn || row.mfg_part_num}</strong></div>
              <div><span className="stat-label">Manufacturer:</span> <strong>{row.identity?.candidate_manufacturer || row.part_manuf}</strong></div>
              <div><span className="stat-label">Brand:</span> <strong>{row.identity?.candidate_brand || "-"}</strong></div>
              <div><span className="stat-label">Category (Classpath):</span> <strong>{row.identity?.candidate_classpath || "-"}</strong></div>
              <div>
                <span className="stat-label" style={{ display: 'block' }}>Official Source URL:</span> 
                <a href={row.identity?.official_source_url} target="_blank" rel="noreferrer" style={{ color: '#3b82f6', wordBreak: 'break-all' }}>
                  {row.identity?.official_source_url || "Not Found"}
                </a>
              </div>
              <div>
                <span className="stat-label">Status:</span> <StatusBadge status={row.identity?.status} />
              </div>
            </div>
          </section>

          {/* Attributes Section */}
          <section className="details-section">
            <h3>Extracted Attributes</h3>
            <div className="table-container">
              <table className="fact-table">
                <thead>
                  <tr>
                    <th>Attribute</th>
                    <th>Raw Value</th>
                    <th>Normalized Value</th>
                    <th>Validation</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {facts.map((fact, idx) => (
                    <tr key={idx}>
                      <td><strong>{fact.attribute}</strong></td>
                      <td>{fact.raw_value}</td>
                      <td>{fact.normalized_value}</td>
                      <td><StatusBadge status={fact.validation_status} /></td>
                      <td>
                        <button 
                          className="secondary btn-small" 
                          onClick={() => setSelectedFact(fact)}
                        >
                          View Evidence
                        </button>
                      </td>
                    </tr>
                  ))}
                  {facts.length === 0 && (
                    <tr><td colSpan={5}>No facts extracted.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* Generated Content Section */}
          {content && (
            <section className="details-section">
              <h3>Generated E-Commerce Content</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <div className="stat-label">Short Description</div>
                  <div>{content.short_description || "-"}</div>
                </div>
                <div>
                  <div className="stat-label">Marketing Description</div>
                  <div>{content.marketing_description || "-"}</div>
                </div>
                <div>
                  <div className="stat-label">Feature Bullets</div>
                  <ul style={{ margin: 0, paddingLeft: '1.2rem', color: 'var(--text-primary)' }}>
                    {content.item_features?.map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                  {(!content.item_features || content.item_features.length === 0) && "-"}
                </div>
              </div>
            </section>
          )}

          {/* Digital Assets Section */}
          <section className="details-section">
            <h3>Digital Assets</h3>
            <div className="assets-grid">
              {assets.map((asset, idx) => (
                <div key={idx} className="asset-card">
                  <div style={{ fontWeight: 'bold' }}>{asset.classification}</div>
                  <a href={asset.url} target="_blank" rel="noreferrer">
                    {asset.url.split("/").pop() || "Link"}
                  </a>
                  <div><StatusBadge status={asset.status} /></div>
                </div>
              ))}
              {assets.length === 0 && <div>No assets mapped.</div>}
            </div>
          </section>
        </div>
      </div>

      {selectedFact && (
        <SourceEvidenceModal
          attribute={selectedFact.attribute}
          evidence_text={selectedFact.evidence_text}
          source_url={selectedFact.source_url}
          source_type={selectedFact.source_type}
          validation_status={selectedFact.validation_status}
          confidence={selectedFact.confidence}
          onClose={() => setSelectedFact(null)}
        />
      )}
    </div>
  );
};

export default ProductDetailsDrawer;
