import { motion } from "framer-motion";
import { theme } from "../theme";
import { metrics } from "../lib/data";
import { fmtInt } from "../lib/format";

export function Hero() {
  const s = metrics.scope;
  const purchases = metrics.funnel.find((f) => f.step === "purchase")?.users ?? 0;
  return (
    <section className="min-h-screen flex flex-col justify-center px-8 max-w-5xl mx-auto">
      <motion.p className="text-sm tracking-widest uppercase mb-4" style={{ color: theme.color.gold }}
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8 }}>
        电商用户行为 · 路径与留存
      </motion.p>
      <motion.h1 className="text-5xl font-extrabold leading-tight" style={{ color: theme.color.ink }}
                 initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}
                 transition={{ duration: theme.duration.slow, ease: theme.ease }}>
        从 {fmtInt(s.users)} 个用户的<br />完整行为旅程里读懂转化
      </motion.h1>
      <div className="flex gap-10 mt-10">
        <Stat label="事件" value={fmtInt(s.rows)} />
        <Stat label="会话" value={fmtInt(s.sessions)} />
        <Stat label="购买用户" value={fmtInt(purchases)} />
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-4xl font-extrabold" style={{ color: theme.color.teal }}>{value}</div>
      <div className="text-sm" style={{ color: theme.color.muted }}>{label}</div>
    </div>
  );
}
