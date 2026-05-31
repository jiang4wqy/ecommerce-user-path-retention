import { useEffect, useRef, useState } from "react";

// 当 active 变 true 时，用 requestAnimationFrame 把数字从 0 滚到 target。
export function useCountUp(target: number, active: boolean, durationMs = 1000): number {
  const [value, setValue] = useState(0);
  const startedRef = useRef(false);

  useEffect(() => {
    if (!active || startedRef.current) return;
    startedRef.current = true;
    if (durationMs <= 0) {
      setValue(target);
      return;
    }
    const start = performance.now();
    let raf = 0;
    const tick = () => {
      // Use performance.now() (not the rAF timestamp) so start and elapsed share
      // one clock — the rAF timestamp can use a different origin under jsdom.
      const t = Math.min(1, (performance.now() - start) / durationMs);
      const eased = 1 - Math.pow(1 - t, 3); // easeOutCubic
      setValue(target * eased);
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [active, target, durationMs]);

  return value;
}
