import { useRef, useState } from "react";
import { useMotionValueEvent } from "framer-motion";
import { useScrollProgress } from "../lib/useScrollProgress";
import { RetentionHeatmap } from "../components/charts/RetentionHeatmap";
import { Takeaway } from "../components/Takeaway";
import { theme } from "../theme";
import { metrics } from "../lib/data";

export function Retention({ onActive }: { onActive: (id: string) => void }) {
  const ref = useRef<HTMLElement>(null);
  const progress = useScrollProgress(ref);
  const [p, setP] = useState(0);
  useMotionValueEvent(progress, "change", (v) => {
    setP(v);
    if (v > 0.05 && v < 0.95) onActive("retention");
  });
  return (
    <section ref={ref} id="retention" className="relative" style={{ height: "200vh" }}>
      <div className="sticky top-0 min-h-screen flex flex-col justify-center px-8 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold mb-8" style={{ color: theme.color.teal }}>Cohort 留存</h2>
        <RetentionHeatmap data={metrics.retention} progress={p} />
        <Takeaway>留存主要发生在首访后一周内（D1 最高、随后衰减）；新用户首周触达最关键。</Takeaway>
      </div>
    </section>
  );
}
