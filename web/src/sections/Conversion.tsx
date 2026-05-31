import { useRef, useState } from "react";
import { useMotionValueEvent } from "framer-motion";
import { useScrollProgress } from "../lib/useScrollProgress";
import { FunnelSticky } from "../components/charts/FunnelSticky";
import { PriceBandChart } from "../components/charts/PriceBandChart";
import { Takeaway } from "../components/Takeaway";
import { theme } from "../theme";
import { metrics } from "../lib/data";
import { fmtPct } from "../lib/format";

export function Conversion({ onActive }: { onActive: (id: string) => void }) {
  const ref = useRef<HTMLElement>(null);
  const progress = useScrollProgress(ref);
  const [p, setP] = useState(0);
  useMotionValueEvent(progress, "change", (v) => {
    setP(v);
    if (v > 0.05 && v < 0.95) onActive("conversion");
  });
  const ca = metrics.cart_abandonment[0] ?? { abandonment_rate: 0 };
  return (
    <section ref={ref} id="conversion" className="relative" style={{ height: "220vh" }}>
      <div className="sticky top-0 min-h-screen flex flex-col justify-center px-8 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold mb-8" style={{ color: theme.color.teal }}>转化漏斗</h2>
        <FunnelSticky data={metrics.funnel} progress={p} />
        <div className="mt-10"><PriceBandChart data={metrics.price_band} active={p > 0.6} /></div>
        <Takeaway>
          加购放弃率约 {fmtPct(ca.abandonment_rate)}；加购未买用户是购物车召回与价格提醒的首选对象。
        </Takeaway>
      </div>
    </section>
  );
}
