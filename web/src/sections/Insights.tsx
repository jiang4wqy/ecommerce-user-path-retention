import { Section } from "../components/Section";
import { motion } from "framer-motion";
import { theme } from "../theme";
import { metrics } from "../lib/data";

export function Insights({ onActive }: { onActive: (id: string) => void }) {
  return (
    <Section id="insights" title="业务洞察与建议" onActive={onActive}>
      {(active) => (
        <div className="flex flex-col gap-4">
          {metrics.insights.map((text, i) => (
            <motion.div key={i} className="rounded-xl px-5 py-4"
              style={{ background: theme.color.surface, border: `1px solid ${theme.color.border}`,
                       borderLeft: `4px solid ${theme.color.gold}`, color: theme.color.ink }}
              initial={{ opacity: 0, x: -20 }}
              animate={active ? { opacity: 1, x: 0 } : {}}
              transition={{ delay: i * 0.12, duration: 0.5, ease: theme.ease }}>
              {text}
            </motion.div>
          ))}
        </div>
      )}
    </Section>
  );
}
