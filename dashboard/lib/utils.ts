
/**
 * Lógica pura de cálculo de Drift para pruebas unitarias.
 * Separada del componente para garantizar trazabilidad matemática.
 */
export function calculateDrift(currentVol: number, historicalVolumes: number[]) {
  const volumes = (historicalVolumes || []).filter(v => v !== null && v !== undefined);
  
  if (volumes.length < 1) return { driftStatus: 'New', driftPct: 0 };
  
  const sumPrev = volumes.reduce((a, b) => a + b, 0);
  const avgVolume = sumPrev / volumes.length;
  
  let pctChange = 0;
  if (avgVolume > 0) {
    pctChange = ((currentVol - avgVolume) / avgVolume) * 100;
  }
  
  if (isNaN(pctChange)) pctChange = 0;
  
  let driftStatus = 'Stable';
  if (Math.abs(pctChange) > 20) {
    driftStatus = pctChange > 0 ? 'Drift Up' : 'Drift Down';
  }
  
  return { 
    driftStatus, 
    driftPct: Math.round(pctChange) 
  };
}

/**
 * Lógica de Forecast Readiness (IA Readiness).
 * Evalúa la salud de tablas críticas y aplica penalizaciones por lag.
 */
export function calculateReadiness(coreEntries: any[]) {
  if (!coreEntries || coreEntries.length === 0) return 0;
  
  const coreAvg = coreEntries.reduce((acc, curr) => acc + (curr.health_score || 0), 0) / coreEntries.length;
  
  // Penalización de 15 puntos si alguna tabla core tiene más de 2 días de lag
  const hasHighLag = coreEntries.some(e => (e.health_report?.time_analysis?.freshness_lag_days || 0) > 2);
  const lagPenalty = hasHighLag ? 15 : 0;
  
  return Math.max(0, Math.round(coreAvg - lagPenalty));
}
