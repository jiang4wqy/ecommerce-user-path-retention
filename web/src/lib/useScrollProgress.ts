import { RefObject } from "react";
import { useScroll, useTransform, MotionValue } from "framer-motion";

// 返回 0→1 的进度：当 ref 元素从进入视口到离开视口顶部的滚动比例。
// 用于驱动钉图（sticky）按进度逐级点亮。
export function useScrollProgress(ref: RefObject<HTMLElement>): MotionValue<number> {
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  });
  return useTransform(scrollYProgress, [0, 1], [0, 1]);
}
