import { useEffect, useRef } from "react";
import type { ReactNode } from "react";
import { motion, useInView } from "framer-motion";
import { theme } from "../theme";

interface SectionProps {
  id: string;
  title: string;
  children: (active: boolean) => ReactNode;
  onActive?: (id: string) => void;
}

export function Section({ id, title, children, onActive }: SectionProps) {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { amount: 0.4, margin: "-20% 0px -20% 0px" });

  useEffect(() => {
    if (inView) onActive?.(id);
  }, [inView, id, onActive]);

  return (
    <section ref={ref} id={id} className="min-h-screen px-8 py-24 max-w-5xl mx-auto">
      <motion.h2
        className="text-3xl font-bold mb-8"
        style={{ color: theme.color.teal }}
        initial={{ opacity: 0, y: 24 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: theme.duration.base, ease: theme.ease }}
      >
        {title}
      </motion.h2>
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: theme.duration.base, ease: theme.ease, delay: 0.1 }}
      >
        {children(inView)}
      </motion.div>
    </section>
  );
}
