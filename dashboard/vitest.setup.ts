import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock de Lucide React para evitar errores con los SVG en el entorno de pruebas
vi.mock('lucide-react', () => ({
  Activity: () => 'ActivityIcon',
  Database: () => 'DatabaseIcon',
  ShieldCheck: () => 'ShieldCheckIcon',
  Clock: () => 'ClockIcon',
  Layers: () => 'LayersIcon',
  TrendingUp: () => 'TrendingUpIcon',
  TrendingDown: () => 'TrendingDownIcon',
  Minus: () => 'MinusIcon',
  Plus: () => 'PlusIcon',
}));

// Mock global de fetch para evitar llamadas reales a red
global.fetch = vi.fn();
