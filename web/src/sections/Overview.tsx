import { Section } from "../components/Section";
import { KpiCard } from "../components/KpiCard";
import { TrendChart } from "../components/charts/TrendChart";
import { Takeaway } from "../components/Takeaway";
import { metrics } from "../lib/data";
import { fmtInt, fmtMoney, fmtPct } from "../lib/format";

export function Overview({ onActive }: { onActive: (id: string) => void }) {
  const d = metrics.daily_kpis;
  const gmv = d.reduce((a, r) => a + (r.gmv || 0), 0);
  const purchases = d.reduce((a, r) => a + (r.purchases || 0), 0);
  const avgConv = d.length ? d.reduce((a, r) => a + (r.purchase_rate || 0), 0) / d.length : 0;
  const dau = d.length ? d.reduce((a, r) => a + (r.dau || 0), 0) / d.length : 0;
  return (
    <Section id="overview" title="整体经营与行为" onActive={onActive}>
      {(active) => (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <KpiCard label="DAU 均值" value={dau} format={fmtInt} active={active} />
            <KpiCard label="总 GMV" value={gmv} format={fmtMoney} active={active} />
            <KpiCard label="平均购买转化" value={avgConv} format={(n) => fmtPct(n, 2)} active={active} />
            <KpiCard label="总购买" value={purchases} format={fmtInt} active={active} />
          </div>
          <div className="mt-8"><TrendChart data={d} active={active} /></div>
          <Takeaway>样本期内活跃、加购与购买同步波动；接下来看转化在哪一步流失。</Takeaway>
        </>
      )}
    </Section>
  );
}
