import { describe, it, expect } from 'vitest';
import { calculateDrift, calculateReadiness } from '../lib/utils';

describe('Dashboard Logic Tests (Unitaries)', () => {
  
  describe('calculateDrift()', () => {
    it('should return Stable for small variations (< 20%)', () => {
      const result = calculateDrift(105, [100, 100, 100]);
      expect(result.driftStatus).toBe('Stable');
      expect(result.driftPct).toBe(5);
    });

    it('should return Drift Up for increases > 20%', () => {
      const result = calculateDrift(150, [100, 100]);
      expect(result.driftStatus).toBe('Drift Up');
      expect(result.driftPct).toBe(50);
    });

    it('should return Drift Down for decreases > 20%', () => {
      const result = calculateDrift(50, [100, 100]);
      expect(result.driftStatus).toBe('Drift Down');
      expect(result.driftPct).toBe(-50);
    });

    it('should return New if no history is provided', () => {
      const result = calculateDrift(100, []);
      expect(result.driftStatus).toBe('New');
    });

    it('should handle zero historical volume gracefully', () => {
      const result = calculateDrift(100, [0, 0]);
      expect(result.driftPct).toBe(0);
      expect(result.driftStatus).toBe('Stable');
    });
  });

  describe('calculateReadiness()', () => {
    it('should return average health score when lag is low', () => {
      const coreEntries = [
        { health_score: 100, health_report: { time_analysis: { freshness_lag_days: 0 } } },
        { health_score: 90, health_report: { time_analysis: { freshness_lag_days: 1 } } }
      ];
      expect(calculateReadiness(coreEntries)).toBe(95);
    });

    it('should apply penalty of 15 points if lag > 2 days', () => {
      const coreEntries = [
        { health_score: 100, health_report: { time_analysis: { freshness_lag_days: 3 } } },
        { health_score: 100, health_report: { time_analysis: { freshness_lag_days: 0 } } }
      ];
      // Average is 100, but lag penalty is 15 -> 85
      expect(calculateReadiness(coreEntries)).toBe(85);
    });

    it('should not return negative values', () => {
      const coreEntries = [
        { health_score: 10, health_report: { time_analysis: { freshness_lag_days: 5 } } }
      ];
      // 10 - 15 would be -5, but we expect 0
      expect(calculateReadiness(coreEntries)).toBe(0);
    });

    it('should return 0 if no entries provided', () => {
      expect(calculateReadiness([])).toBe(0);
    });
  });
});
