export const theme = {
  color: {
    canvas: "#faf6ef",
    surface: "#fffdf8",
    ink: "#2b2117",
    muted: "#7a6a52",
    border: "#e6dcc8",
    teal: "#0f5e57",
    gold: "#c79a3a",
    clay: "#b06a3c",
  },
  // 图表统一色序
  series: ["#0f5e57", "#c79a3a", "#b06a3c", "#3f6f8f", "#8fa99d", "#6f5b3e"],
  radius: 12,
  shadow: "0 12px 28px rgba(43, 33, 23, 0.08)",
  ease: [0.22, 1, 0.36, 1] as const, // 统一缓动（easeOutExpo 风格）
  duration: { base: 0.6, slow: 1.1 },
} as const;

export type Theme = typeof theme;
