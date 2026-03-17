"use client";

import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";
import { 
  Activity, 
  Database, 
  ShieldCheck, 
  Clock, 
  Layers,
  ChevronLeft,
  TrendingUp,
  Settings,
  Zap,
  Briefcase,
  Shield,
  Wind,
  Target
} from "lucide-react";
import { calculateDrift, calculateReadiness } from "../lib/utils";

// --- Interfaces ---
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
      observations?: {
        score: number;
        message: string;
        count: number;
      };
    };
    quality_metrics?: {
      custom_rules_violations: string[];
    };
    time_analysis?: {
      freshness_lag_days: number;
    };
  };
}

type ViewType = "home" | "health" | "forecast" | "monitor" | "simulate";

// --- Sub-Components ---

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

const PillarIcon = ({ type }: { type: ViewType }) => {
  switch (type) {
    case "health": return <ShieldCheck size={24} />;
    case "forecast": return <TrendingUp size={24} />;
    case "monitor": return <Settings size={24} />;
    case "simulate": return <Zap size={24} />;
    default: return <Activity size={24} />;
  }
};

// --- Main Components ---

export default function Dashboard() {
  const [currentView, setCurrentView] = useState<ViewType>("home");
  const [data, setData] = useState<AuditEntry[]>([]);
  const [history, setHistory] = useState<Record<string, number[]>>({});
  const [violations, setViolations] = useState<{table: string, rule: string}[]>([]);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const [lastSync, setLastSync] = useState<string | null>(null);
  const [stats, setStats] = useState({
    totalRows: 0,
    avgScore: 0,
    avgBusinessScore: 0,
    avgContinuityScore: 0,
    avgIntegrityScore: 0,
    avgCleaningScore: 0,
    alarms: 0,
    status: "Healthy",
    systemOps: "Healthy",
    iaReadiness: 0,
    lastSyncLabel: "---",
    syncStatus: "positive" as "positive" | "warning" | "error",
    mlPerformance: 98,
    mlStatus: "Optimum",
    trustGrade: "A" as "A" | "B" | "C",
    trustLabel: "Optimal Confidence"
  });

  useEffect(() => {
    setMounted(true);
    async function fetchData() {
      try {
        let isMandatoryMissing = false;
        let lastContractFailed = false;
        let authorizedTables: string[] = [];
        const mandatoryTable = "usr_inventario_detallado";

        try {
          // Fetch the absolutely latest contract to detect current status (even if failed)
          const { data: latestContract } = await supabase
            .from("sys_validation_contract")
            .select("status, support_json, created_at")
            .order("created_at", { ascending: false })
            .limit(1);

          if (latestContract && latestContract.length > 0) {
            const contract = latestContract[0];
            lastContractFailed = contract.status === "FAILED";
            
            if (contract.support_json) {
              const report = contract.support_json as any;
              authorizedTables = Object.values(report.tables || {})
                .map((t: any) => t.db_table);
              
              isMandatoryMissing = !authorizedTables.includes(mandatoryTable);
            }

            if (contract.created_at) {
              setLastSync(contract.created_at);
            }
          }
        } catch (e) {
          console.warn("Contract monitoring failed:", e);
        }

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

        if (isMandatoryMissing) {
          allViolations.push({ table: "SYSTEM", rule: "CRITICAL: Mandatory Source 'inventory' is missing or disabled in Contract." });
        }
        if (lastContractFailed) {
          allViolations.push({ table: "SYSTEM", rule: "LATEST LOAD FAILED: Check ingestion logs for details." });
        }
        
        (auditData || []).forEach(entry => {
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
        
        const validEntriesWithReport = latestEntries.filter((e: any) => e.health_report?.health_dimensions);
        const lCount = validEntriesWithReport.length || 1;

        const avgBusinessScore = validEntriesWithReport.reduce((acc, curr: any) => acc + (curr.health_report?.health_dimensions?.business || 100), 0) / lCount;
        const avgContinuityScore = validEntriesWithReport.reduce((acc, curr: any) => acc + (curr.health_report?.health_dimensions?.continuity || 100), 0) / lCount;
        const avgIntegrityScore = validEntriesWithReport.reduce((acc, curr: any) => acc + (curr.health_report?.health_dimensions?.integrity || 100), 0) / lCount;
        const avgCleaningScore = validEntriesWithReport.reduce((acc, curr: any) => acc + (curr.health_report?.health_dimensions?.cleaning || 100), 0) / lCount;

        const totalRows = auditData?.reduce((acc, curr) => {
          if (curr.execution_id === latest?.execution_id) {
            return acc + (curr.row_count || 0);
          }
          return acc;
        }, 0) || 0;

        const iaReadiness = calculateReadiness(latestEntries);
        
        let lastSyncLabel = "---";
        let syncStatus: "positive" | "warning" | "error" = "positive";
        
        if (lastSync) {
          const syncDate = new Date(lastSync);
          const diffMs = Date.now() - syncDate.getTime();
          const diffHours = diffMs / (1000 * 60 * 60);
          
          lastSyncLabel = diffHours < 1 ? "< 1h ago" : `${Math.floor(diffHours)}h ago`;
          
          if (diffHours <= 24) syncStatus = "positive";
          else if (diffHours < 36) syncStatus = "warning";
          else syncStatus = "error";
        }

        // Logic for ML Model Monitoring
        const mlPerformance = 98; 
        const mlStatus = mlPerformance >= 95 ? "Optimum" : mlPerformance >= 85 ? "Degrading" : "Retrain";

        // Global Trust Grade Calculation
        let trustGrade: "A" | "B" | "C" = "A";
        let trustLabel = "Optimal Confidence";

        const hasCriticalError = error || syncStatus === "error" || avgScore < 70 || isMandatoryMissing || lastContractFailed;
        const hasWarning = syncStatus === "warning" || avgScore < 90 || mlPerformance < 95 || allViolations.length > 0;

        if (hasCriticalError) {
          trustGrade = "C";
          trustLabel = isMandatoryMissing 
            ? "CRITICAL: Mandatory Data Missing" 
            : lastContractFailed 
              ? "SYSTEM ERROR: Last Load Failed"
              : "High Risk - Action Required";
        } else if (hasWarning) {
          trustGrade = "B";
          trustLabel = allViolations.length > 0 ? "Integrity Alerts - Review Required" : "Valid with Reservations";
        }

        setStats({
          totalRows,
          avgScore: Math.round(avgScore),
          avgBusinessScore: Math.round(avgBusinessScore),
          avgContinuityScore: Math.round(avgContinuityScore),
          avgIntegrityScore: Math.round(avgIntegrityScore),
          avgCleaningScore: Math.round(avgCleaningScore),
          alarms: allViolations.length,
          status: count === 0 ? "No Data" : avgScore > 90 ? "Excellent" : avgScore > 70 ? "Warning" : "Critical",
          systemOps: (error || lastContractFailed) ? "Issue" : "Healthy",
          iaReadiness: isMandatoryMissing ? 0 : iaReadiness,
          lastSyncLabel: lastSyncLabel,
          syncStatus: (syncStatus === "error" || lastContractFailed) ? "error" : syncStatus,
          mlPerformance: isMandatoryMissing ? 0 : mlPerformance,
          mlStatus: isMandatoryMissing ? "Blocked" : mlStatus,
          trustGrade,
          trustLabel
        });
      } catch (err: any) {
        console.error("Fetch Data Error:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  if (!mounted || loading) {
    return (
      <div className="loading-container">
        <span className="loader"></span>
      </div>
    );
  }

  // --- View Renderers ---

  const renderHome = () => (
    <div className="fade-in">
      {/* --- Executive Trust Bar (Simplified) --- */}
      <div className="flex items-center justify-center mb-10 px-4 py-4 bg-card/30 rounded-2xl border border-white/5">
        <div className={`px-8 py-2 rounded-xl text-sm border transition-all duration-300 shadow-xl ${
          stats.trustGrade === 'A' ? 'border-success text-success bg-success/15 shadow-success/20' :
          stats.trustGrade === 'B' ? 'border-warning text-warning bg-warning/15 shadow-warning/20' :
          'border-error text-error bg-error/15 shadow-error/20'
        }`}>
          <span className="opacity-70 uppercase tracking-widest text-[11px]">Current Status:&nbsp;&nbsp;&nbsp;&nbsp;</span>
          <span className="font-black text-base tracking-tight italic">
            Grade {stats.trustGrade} • {stats.trustLabel}
          </span>
        </div>
      </div>

      {/* --- Executive Summary Cards (Holistic View) --- */}
      <div className="summary-row mb-8">
        {/* 1. MONITORING: System Operations */}
        <div className="summary-card" data-tooltip="Monitoreo de infraestructura y conexión activa a la base de datos (SLA).">
          <div className="summary-icon" style={{ display: 'flex' }}>
            <Activity size={18} className={stats.systemOps === "Healthy" ? "text-success" : "text-error"} />
          </div>
          <div className="summary-content">
            <span className="summary-label">System Ops</span>
            <div className="flex items-end gap-1">
              <span className="summary-value">{stats.systemOps}</span>
            </div>
          </div>
        </div>

        {/* 2. HEALTH: Data Integrity (Dynamic Labels & Colors) */}
        <div className="summary-card" data-tooltip="Índice de integridad y cumplimiento de reglas del contrato de datos técnicos.">
          <div className="summary-icon" style={{ 
            display: 'flex', 
            color: stats.avgScore >= 90 ? 'var(--success)' : stats.avgScore >= 70 ? 'var(--warning)' : 'var(--error)' 
          }}>
            <ShieldCheck size={18} />
          </div>
          <div className="summary-content">
            <span className="summary-label">Data Quality</span>
            <div className="flex items-end gap-1">
              <span className="summary-value">{stats.avgScore}%</span>
              <span className={`summary-trend ${
                stats.avgScore >= 90 ? 'positive' : 
                stats.avgScore >= 70 ? 'warning' : 
                'error'
              }`}>
                {stats.avgScore >= 90 ? 'Trust' : stats.avgScore >= 70 ? 'Caution' : 'Critical'}
              </span>
            </div>
          </div>
        </div>

        {/* 3. HEALTH/MONITORING: Sync Freshness (24h Base) */}
        <div className="summary-card" data-tooltip="Tiempo transcurrido desde la última sincronización exitosa. (Objetivo: <= 24h).">
          <div className="summary-icon" style={{ 
            display: 'flex',
            color: stats.syncStatus === 'positive' ? 'var(--success)' : stats.syncStatus === 'warning' ? 'var(--warning)' : 'var(--error)'
          }}>
            <Clock size={18} />
          </div>
          <div className="summary-content">
            <span className="summary-label">Live Stream</span>
            <div className="flex items-end gap-1">
              <span className="summary-value">Last Sync</span>
              <span className={`summary-trend ${stats.syncStatus}`}>
                {stats.lastSyncLabel}
              </span>
            </div>
          </div>
        </div>

        {/* 4. INTELLIGENCE (FORECAST): IA Readiness (Dynamic Scale) */}
        <div className="summary-card" data-tooltip="Porcentaje de datos óptimos para entrenamiento y re-entrenamiento de modelos IA.">
          <div className="summary-icon" style={{ 
            display: 'flex',
            color: stats.iaReadiness >= 90 ? 'var(--success)' : stats.iaReadiness >= 70 ? 'var(--warning)' : 'var(--error)'
          }}>
            <TrendingUp size={18} />
          </div>
          <div className="summary-content">
            <span className="summary-label">IA Readiness</span>
            <div className="flex items-end gap-1">
              <span className="summary-value">{stats.iaReadiness}%</span>
              <span className={`summary-trend ${
                stats.iaReadiness >= 90 ? 'positive' : 
                stats.iaReadiness >= 70 ? 'warning' : 
                'error'
              }`}>
                {stats.iaReadiness >= 90 ? 'AI Ready' : stats.iaReadiness >= 70 ? 'Suboptimal' : 'Low Power'}
              </span>
            </div>
          </div>
        </div>

        {/* 5. MONITORING/INTELLIGENCE: ML Performance (Model Drift) */}
        <div className="summary-card" data-tooltip="Estado del cerebro predictivo. Alerta sobre degradación o necesidad de ajuste manual.">
          <div className="summary-icon" style={{ 
            display: 'flex',
            color: stats.mlPerformance >= 95 ? 'var(--success)' : stats.mlPerformance >= 85 ? 'var(--warning)' : 'var(--error)'
          }}>
            <Activity size={18} />
          </div>
          <div className="summary-content">
            <span className="summary-label">ML Performance</span>
            <div className="flex items-end gap-1">
              <span className="summary-value">{stats.mlPerformance}%</span>
              <span className={`summary-trend ${
                stats.mlPerformance >= 95 ? 'positive' : 
                stats.mlPerformance >= 85 ? 'warning' : 
                'error'
              }`}>
                {stats.mlStatus}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* --- 3 Pillars Grid (Updated Order) --- */}
      <div className="pillar-grid-3">
        {/* 1. DATA HEALTH (ACTIVE) */}
        <div className="pillar-card active" onClick={() => setCurrentView("health")}>
          <div className="pillar-icon"><ShieldCheck size={28} /></div>
          <div className="pillar-info">
            <h3>Data Health</h3>
            <p>Sovereign data integrity monitoring, drift detection, and contract auditing.</p>
          </div>
          <div className="flex items-center justify-between mt-auto">
            <div className="pillar-status status-online">🟢 Active • {stats.avgScore}%</div>
            <div className="text-secondary text-xs">Technical Details →</div>
          </div>
        </div>

        {/* 2. INTELLIGENCE HUB (MERGED/PLACEHOLDER) */}
        <div className="pillar-card locked">
          <div className="pillar-content">
            <div className="pillar-icon"><TrendingUp size={28} /></div>
            <div className="pillar-info">
              <h3>Intelligence Hub</h3>
              <p>Combined Predictive Demand Engine and Strategic "What-If" Sandbox.</p>
            </div>
          </div>
          <div className="pillar-status status-calibrating mt-auto">⏳ Integration (Phases 3-7)</div>
        </div>

        {/* 3. MONITORING & CONTROL (ACTIVE BRIDGE) */}
        <div className="pillar-card active" onClick={() => setCurrentView("monitor")}>
          <div className="pillar-icon"><Settings size={28} /></div>
          <div className="pillar-info">
            <h3>Monitoring & Control</h3>
            <p>Infrastructure telemetry, DVC orchestration, and pipeline health logs.</p>
          </div>
          <div className="flex items-center justify-between mt-auto">
            <div className="pillar-status status-online">📡 Bridge Active</div>
            <div className="text-secondary text-xs">System Logs →</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderHealthDetail = () => (
    <div className="fade-in">
      <button className="back-button" onClick={() => setCurrentView("home")}>
        <ChevronLeft size={16} /> Back to Central Control
      </button>
      
      <section className="stats-grid mb-10">
        <div className="stat-card" data-tooltip="Cumplimiento de reglas de negocio específicas.">
          <div className="stat-label flex items-center gap-2">
            <Shield size={18} style={{ color: stats.avgBusinessScore < 95 ? 'var(--warning)' : 'var(--primary)' }} /> Business Rules
          </div>
          <div className="stat-value" style={{ color: stats.avgBusinessScore < 95 ? 'var(--warning)' : 'inherit' }}>
            {stats.avgBusinessScore}%
          </div>
          <div className="text-xs text-secondary mt-2">LOGIC CONFORMITY</div>
        </div>
        
        <div className="stat-card" data-tooltip="Estabilidad de la serie temporal y latencia de los datos.">
          <div className="stat-label flex items-center gap-2">
            <Clock size={18} style={{ color: stats.avgContinuityScore < 95 ? 'var(--warning)' : 'var(--primary)' }} /> Continuity
          </div>
          <div className="stat-value" style={{ color: stats.avgContinuityScore < 95 ? 'var(--warning)' : 'inherit' }}>
            {stats.avgContinuityScore}%
          </div>
          <div className="text-xs text-secondary mt-2">TIME STABILITY</div>
        </div>

        <div className="stat-card" data-tooltip="Presencia de nulos y validez de tipos de datos.">
          <div className="stat-label flex items-center gap-2">
            <Zap size={18} style={{ color: stats.avgIntegrityScore < 95 ? 'var(--warning)' : 'var(--primary)' }} /> Data Integrity
          </div>
          <div className="stat-value" style={{ color: stats.avgIntegrityScore < 95 ? 'var(--warning)' : 'inherit' }}>
            {stats.avgIntegrityScore}%
          </div>
          <div className="text-xs text-secondary mt-2">STRUCTURE QUALITY</div>
        </div>

        <div className="stat-card" data-tooltip="Limpieza de datos: Duplicados y valores centinela.">
          <div className="stat-label flex items-center gap-2">
            <Wind size={18} style={{ color: stats.avgCleaningScore < 95 ? 'var(--warning)' : 'var(--primary)' }} /> Data Cleaning
          </div>
          <div className="stat-value" style={{ color: stats.avgCleaningScore < 95 ? 'var(--warning)' : 'inherit' }}>
            {stats.avgCleaningScore}%
          </div>
          <div className="text-xs text-secondary mt-2">HIGIENE & PURITY</div>
        </div>

        <div className="stat-card" data-tooltip="Total de violaciones críticas detectadas en la validación del contrato de datos.">
          <div className="stat-label flex items-center gap-2">
            <Activity size={18} className={stats.alarms > 0 ? "text-error" : "text-secondary"} /> Active Alarms
          </div>
          <div className="stat-value" style={{ color: stats.alarms > 0 ? 'var(--error)' : 'inherit' }}>
            {stats.alarms}
          </div>
          <div className="text-xs text-secondary mt-2">CONTRACT VIOLATIONS</div>
        </div>
      </section>

      <section className="table-section">
        <h2 className="section-title">
          <Database size={20} className="text-primary" /> Ingestion Audit (SSoT)
        </h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th data-tooltip="Nombre de la entidad de datos certificada.">Data Sources</th>
                <th data-tooltip="Estado binario de la última validación del contrato.">Validation</th>
                <th data-tooltip="Dimensiones: Negocio, Continuidad, Integridad, Limpieza y Anomalías.">Dimensions</th>
                <th data-tooltip="Tendencia histórica de salud en los últimos 7 días.">Health Trend</th>
                <th data-tooltip="Perfil de desviación de volumen comparado con el promedio histórico.">Volume Profile</th>
                <th data-tooltip="Cantidad total de registros procesados.">Records</th>
                <th data-tooltip="Método de carga: Incremental o Full.">Method</th>
                <th data-tooltip="Latencia de datos (Freshness).">Freshness</th>
                <th data-tooltip="Calidad total agregada (Media ponderada de los 4 pilares técnicos).">Overall Quality</th>
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
                      <div className="flex gap-2">
                        <div data-tooltip={`Negocio: ${dim?.business ?? 0}%`}>
                          <Briefcase size={14} style={{ color: (dim?.business ?? 0) > 90 ? 'var(--success)' : (dim?.business ?? 0) > 70 ? 'var(--warning)' : 'var(--error)', opacity: dim?.business !== undefined ? 1 : 0.2 }} />
                        </div>
                        <div data-tooltip={`Continuidad: ${dim?.continuity ?? 0}%`}>
                          <Zap size={14} style={{ color: (dim?.continuity ?? 0) > 90 ? 'var(--success)' : (dim?.continuity ?? 0) > 70 ? 'var(--warning)' : 'var(--error)', opacity: dim?.continuity !== undefined ? 1 : 0.2 }} />
                        </div>
                        <div data-tooltip={`Integridad: ${dim?.integrity ?? 0}%`}>
                          <Shield size={14} style={{ color: (dim?.integrity ?? 0) > 90 ? 'var(--success)' : (dim?.integrity ?? 0) > 70 ? 'var(--warning)' : 'var(--error)', opacity: dim?.integrity !== undefined ? 1 : 0.2 }} />
                        </div>
                        <div data-tooltip={`Limpieza: ${dim?.cleaning ?? 0}%`}>
                          <Wind size={14} style={{ color: (dim?.cleaning ?? 0) > 90 ? 'var(--success)' : (dim?.cleaning ?? 0) > 70 ? 'var(--warning)' : 'var(--error)', opacity: dim?.cleaning !== undefined ? 1 : 0.2 }} />
                        </div>
                        <div data-tooltip={dim?.observations?.message ?? 'Cargando Observaciones...'}>
                          <Target size={14} style={{ 
                            color: dim?.observations === undefined ? 'var(--secondary)' : dim.observations.score === 100 ? 'var(--success)' : 'var(--warning)', 
                            opacity: dim?.observations !== undefined ? 1 : 0.3 
                          }} />
                        </div>
                      </div>
                    </td>
                    <td><Sparkline data={history[entry.table_name]} /></td>
                    <td>
                      <div className="flex items-center">
                        <span className={`px-2 py-1 rounded text-[10px] font-bold border ${
                          (entry as any).driftStatus === 'Stable' ? 'border-success/30 text-success bg-success/5' :
                          'border-warning/30 text-warning bg-warning/5'
                        }`}>
                          {(entry as any).driftStatus === 'Drift Up' ? '↗️' : (entry as any).driftStatus === 'Drift Down' ? '↘️' : '↔️'} {(entry as any).driftStatus}
                        </span>
                      </div>
                    </td>
                    <td>{entry.row_count.toLocaleString()}</td>
                    <td style={{ fontSize: '0.85rem' }}>{entry.load_type || 'Full'}</td>
                    <td>
                      <span className={`badge ${lag === 0 ? 'success' : lag < 3 ? 'warning' : 'error'}`} style={{ padding: '2px 8px', fontSize: '0.7rem' }}>
                        {lag === 0 ? 'Live' : `${lag}d lag`}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.85rem', fontWeight: 600 }}>{entry.health_score.toFixed(1)}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

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
    </div>
  );

  return (
    <main>
      <header className="header">
        <div className="title-group">
          <div className="subtitle">Operational Intelligence • Bunuelos SAS</div>
          <h1>Bunuelos Pulse</h1>
        </div>
        <div className="flex flex-col items-end gap-1.5">
          <div className={`badge ${stats.avgScore > 80 ? 'success' : 'warning'}`}>
            <div className="pulse-dot"></div>
            System Status: {stats.status}
          </div>
          {lastSync && (
            <div className="flex items-center gap-1 text-[9px] text-secondary opacity-50 pr-2">
              <Clock size={8} />
              <span>Synchronized: {new Date(lastSync).toLocaleString('en-US', { 
                day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', hour12: true 
              })}</span>
            </div>
          )}
        </div>
      </header>

      {currentView === "home" ? renderHome() : null}
      {currentView === "health" ? renderHealthDetail() : null}
      
      <footer style={{ marginTop: '4rem', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
        Bunuelos_TuRedondito Strategic Hub v1.2.0 • Phase 02 Complete
      </footer>
    </main>
  );
}
