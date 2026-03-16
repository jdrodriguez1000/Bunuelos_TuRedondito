"use client";

import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";
import { 
  Activity, 
  Database, 
  ShieldCheck, 
  Clock, 
  Layers
} from "lucide-react";
import { calculateDrift, calculateReadiness } from "../lib/utils";


interface AuditEntry {
  id: string;
  table_name: string;
  status: string;
  health_score: number;
  row_count: number;
  created_at: string;
  load_type: string;
  execution_id: string;
  health_report?: {
    health_dimensions?: {
      business: number;
      continuity: number;
      integrity: number;
      cleaning: number;
    };
    quality_metrics?: {
      custom_rules_violations: string[];
    };
    time_analysis?: {
      freshness_lag_days: number;
    };
  };
}

const Sparkline = ({ data }: { data: number[] }) => {
  if (!data || data.length < 2) return <div className="text-xs text-secondary">New</div>;
  const max = 100;
  const width = 60;
  const height = 20;
  const points = data.map((v, i) => `${(i / (data.length - 1)) * width},${height - (v / max) * height}`).join(' ');
  
  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline
        fill="none"
        stroke="var(--primary)"
        strokeWidth="1.5"
        strokeLinejoin="round"
        points={points}
        style={{ filter: 'drop-shadow(0 0 2px var(--primary))' }}
      />
    </svg>
  );
};

export default function Dashboard() {
  const [data, setData] = useState<AuditEntry[]>([]);
  const [history, setHistory] = useState<Record<string, number[]>>({});
  const [violations, setViolations] = useState<{table: string, rule: string}[]>([]);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const [stats, setStats] = useState({
    totalRows: 0,
    avgScore: 0,
    avgBusinessScore: 0,
    alarms: 0,
    status: "Healthy"
  });

  useEffect(() => {
    setMounted(true);
    async function fetchData() {
      try {
        // 1. Obtener lista de tablas autorizadas desde el Contrato en Supabase (SSoT Cloud)
        let authorizedTables: string[] = [];
        try {
          const { data: contractData } = await supabase
            .from("sys_validation_contract")
            .select("support_json")
            .eq("status", "VALID")
            .order("created_at", { ascending: false })
            .limit(1);
          
          if (contractData && contractData[0]?.support_json) {
            const contract = contractData[0].support_json as any;
            // Extraer tablas habilitadas del contrato
            authorizedTables = (contract.sources?.inventory?.tables || [])
              .filter((t: any) => t.enabled !== false)
              .map((t: any) => t.db_table);
          }
        } catch (e) {
          console.warn("No se pudo cargar el contrato desde Supabase, usando descubrimiento por prefijo.");
        }

        // 2. Obtener auditoría
        const { data: auditData, error } = await supabase
          .from("sys_ingestion_audit")
          .select("*")
          .order("created_at", { ascending: false })
          .limit(100);

        if (error) throw error;

        const latestEntries: AuditEntry[] = [];
        const seenTables = new Set();
        const tableTrends: Record<string, number[]> = {};
        const tableHistoryVolumes: Record<string, number[]> = {};
        const allViolations: {table: string, rule: string}[] = [];
        
        (auditData || []).forEach(entry => {
          // Portero Dinámico: 
          // Si tenemos lista del contrato en la nube, la usamos. Si no, usamos el prefijo 'usr_'
          const isAuthorized = authorizedTables.length > 0 
            ? authorizedTables.includes(entry.table_name)
            : entry.table_name.startsWith('usr_');

          if (!isAuthorized) return;

          if (!tableTrends[entry.table_name]) {
            tableTrends[entry.table_name] = [];
            tableHistoryVolumes[entry.table_name] = [];
          }
          if (tableTrends[entry.table_name].length < 10) {
            tableTrends[entry.table_name].unshift(entry.health_score);
            tableHistoryVolumes[entry.table_name].push(entry.row_count);
          }
          
          if (!seenTables.has(entry.table_name)) {
            seenTables.add(entry.table_name);
            latestEntries.push(entry);
            const rules = entry.health_report?.quality_metrics?.custom_rules_violations || [];
            rules.forEach((rule: string) => allViolations.push({ table: entry.table_name, rule }));
          }
        });

        // Enhancing latestEntries with robust Drift Calculation
        const entriesWithDrift = latestEntries.map(entry => {
          const historicalVolumes = (tableHistoryVolumes[entry.table_name] || []).slice(1);
          const drift = calculateDrift(entry.row_count || 0, historicalVolumes);
          return { ...entry, ...drift };
        });


        setData(entriesWithDrift as any);
        setHistory(tableTrends);
        setViolations(allViolations);
        
        const latest = auditData?.[0];
        const count = auditData?.length || 0;
        const avgScore = count > 0 
          ? auditData!.reduce((acc, curr) => acc + (curr.health_score || 0), 0) / count 
          : 0;
        
        const avgBusinessScore = latestEntries.length > 0
          ? latestEntries.reduce((acc, curr) => acc + (curr.health_report?.health_dimensions?.business || 100), 0) / latestEntries.length
          : 0;



        // Calculate total rows from the latest execution batch instead of a strict calendar check
        const totalRows = auditData?.reduce((acc, curr) => {
          if (curr.execution_id === latest?.execution_id) {
            return acc + (curr.row_count || 0);
          }
          return acc;
        }, 0) || 0;

        setStats({
          totalRows,
          avgScore: Math.round(avgScore),
          avgBusinessScore: Math.round(avgBusinessScore),
          alarms: allViolations.length,
          status: count === 0 ? "No Data" : avgScore > 90 ? "Excellent" : avgScore > 70 ? "Warning" : "Critical"
        });
      } catch (err: any) {
        console.error("Full Error Object:", err);
        console.error("Error name:", err.name);
        console.error("Error message:", err.message);
        if (err.stack) console.error("Error stack:", err.stack);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Prevent hydration mismatch by wait for mount
  if (!mounted || loading) {
    return (
      <div className="loading-container">
        <span className="loader"></span>
      </div>
    );
  }

  return (
    <main>
      <header className="header">
        <div className="title-group">
          <div className="subtitle">Operational Intelligence</div>
          <h1>Bunuelos Pulse</h1>
        </div>
        <div className={`badge ${stats.avgScore > 80 ? 'success' : 'warning'}`}>
          <div className="pulse-dot"></div>
          System Status: {stats.status}
        </div>
      </header>

      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-label flex items-center gap-2">
            <ShieldCheck size={16} className="text-primary" /> Integrity Score
          </div>
          <div className="stat-value">{stats.avgScore}%</div>
          <div className="text-xs text-secondary mt-2">Avg. Health across tables</div>
        </div>

        <div className="stat-card">
          <div className="stat-label flex items-center gap-2">
            <Layers size={16} className="text-primary" /> Daily Rows Ingested
          </div>
          <div className="stat-value">{stats.totalRows.toLocaleString()}</div>
          <div className="text-xs text-secondary mt-2">Today's physical volume</div>
        </div>

        <div className="stat-card">
          <div className="stat-label flex items-center gap-2">
            <Activity size={16} className="text-secondary" /> Active Alarms
          </div>
          <div className="stat-value" style={{ color: stats.alarms > 0 ? '#ff4d4d' : 'inherit' }}>
            {stats.alarms}
          </div>
          <div className="text-xs text-secondary mt-2">Critical contract violations</div>
        </div>


        <div className="stat-card">
          <div className="stat-label flex items-center gap-2">
            <Database size={16} style={{ color: stats.avgBusinessScore < 95 ? '#ff4d4d' : 'var(--primary)' }} /> Business Score
          </div>
          <div className="stat-value" style={{ color: stats.avgBusinessScore < 95 ? '#ff4d4d' : 'inherit' }}>
            {stats.avgBusinessScore}%
          </div>
          <div className="text-xs text-secondary mt-2">Business rules compliance</div>
        </div>
      </section>

      <section className="table-section">
        <h2 className="section-title">
          <Database size={20} className="text-primary" /> Latest Ingestion Audit
        </h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Table Name</th>
                <th>Status</th>
                <th>Health Pillars</th>
                <th>Trend</th>
                <th>Drift Status</th>
                <th>Rows</th>
                <th>Load Type</th>
                <th>Freshness</th>
                <th>Health Score</th>
              </tr>
            </thead>
            <tbody>
              {data.map((entry) => {
                const dim = entry.health_report?.health_dimensions;
                const lag = entry.health_report?.time_analysis?.freshness_lag_days ?? 0;
                
                return (
                  <tr key={entry.id}>
                    <td style={{ fontWeight: 600 }}>{entry.table_name}</td>
                    <td>
                      <span className={`status-pill ${entry.status.toLowerCase() === 'success' ? 'success' : 'error'}`}>
                        {entry.status}
                      </span>
                    </td>
                    <td>
                      <div className="dimension-row" style={{ display: 'flex', gap: '4px' }}>
                        {[dim?.business, dim?.continuity, dim?.integrity, dim?.cleaning].map((v, i) => (
                          <div 
                            key={i} 
                            title={`Dimension ${i}: ${v}%`}
                            style={{ 
                              width: '20px', 
                              height: '8px', 
                              borderRadius: '2px',
                              background: v !== undefined ? (v > 90 ? 'var(--success)' : v > 70 ? 'var(--warning)' : '#ff4d4d') : '#333'
                            }}
                          />
                        ))}
                      </div>
                    </td>
                    <td>
                      <Sparkline data={history[entry.table_name]} />
                    </td>
                    <td>
                      <div className="flex flex-col">
                        <span className={`text-xs font-bold ${(entry as any).driftStatus?.includes('Drift') ? 'text-warning' : 'text-success'}`}>
                          {(entry as any).driftStatus === 'Drift Up' ? '⬆️ Drift' : (entry as any).driftStatus === 'Drift Down' ? '⬇️ Drift' : '↔️ Stable'}
                        </span>
                        {(entry as any).driftStatus !== 'New' && (
                          <span className="text-secondary" style={{ fontSize: '0.65rem' }}>
                            {Math.abs((entry as any).driftPct)}% variance
                          </span>
                        )}
                      </div>
                    </td>
                    <td>{entry.row_count.toLocaleString()}</td>
                    <td style={{ fontSize: '0.85rem' }}>{entry.load_type || 'Full'}</td>
                    <td>
                      <span className={`badge ${lag === 0 ? 'success' : lag < 3 ? 'warning' : 'error'}`} style={{ padding: '2px 8px', fontSize: '0.7rem' }}>
                        {lag === 0 ? 'Live' : `${lag}d lag`}
                      </span>
                    </td>
                    <td>
                      <div className="flex flex-col items-center">
                        <span 
                          className={`badge ${entry.health_score > 90 ? 'success' : entry.health_score > 70 ? 'warning' : 'error'}`}
                          style={{ padding: '2px 8px', fontSize: '0.7rem', fontWeight: 600 }}
                        >
                          {entry.health_score > 90 ? 'Excellent' : entry.health_score > 70 ? 'Good' : 'Critical'}
                        </span>
                        <span className="text-secondary" style={{ fontSize: '0.65rem', marginTop: '2px' }}>
                          {entry.health_score.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {violations.length > 0 && (
          <div style={{ marginTop: '2rem', background: 'rgba(255, 77, 77, 0.05)', border: '1px solid rgba(255, 77, 77, 0.2)', borderRadius: '12px', padding: '1.5rem' }}>
            <h3 style={{ color: '#ff4d4d', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem', fontSize: '1rem' }}>
              <ShieldCheck size={18} /> Business Rules Violations (Latest Batch)
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
              {violations.map((v, i) => (
                <div key={i} className="violation-item" style={{ background: 'rgba(255,255,255,0.03)', padding: '0.8rem', borderRadius: '8px', fontSize: '0.85rem', borderLeft: '3px solid #ff4d4d' }}>
                  <span style={{ fontWeight: 700, opacity: 0.7 }}>{v.table}:</span> {v.rule}
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      <footer style={{ marginTop: '4rem', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
        Bunuelos_TuRedondito Pipeline Protocol v1.1.0 • Powered by Supabase & Vercel
      </footer>
    </main>
  );
}
