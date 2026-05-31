import raw from "../data/metrics.json";

export interface Metrics {
  daily_kpis: any[];
  funnel: any[];
  retention: any[];
  paths: any[];
  purchase_paths: any[];
  segments: any[];
  session_depth: any[];
  category: any[];
  price_band: any[];
  cart_abandonment: any[];
  scope: { rows: number; users: number; sessions: number; date_range: { min?: string; max?: string } };
  insights: string[];
}

export const metrics = raw as unknown as Metrics;
