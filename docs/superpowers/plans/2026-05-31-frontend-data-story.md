# 前端数据故事页 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有 Python/Streamlit 项目旁新增一个独立的只读「数据故事」展示页（`web/`），读取同一套已算好的指标，做成有动画、有叙事、暖调轻奢配色、视觉统一的高级展示页。

**Architecture:** Python 端新增 `export_web_data.py` 把 `data/processed/metrics/*.csv` 烘焙成单一 `web/src/data/metrics.json`（前端唯一数据源，保证数值一致）。前端是 Vite + React + TS 单页：左侧进度轴 + 竖向长卷叙事为骨架，漏斗/留存两个板块用「钉图」（sticky）随滚动逐级点亮。配色/间距/缓动集中在 `theme.ts`。

**Tech Stack:** Vite, React 18, TypeScript, Tailwind CSS, Framer Motion（动画/滚动）, Recharts（标准图）, 自定义 SVG（漏斗/留存钉图）, Vitest + React Testing Library（前端测试）, pytest（数据烘焙一致性）。

参考设计文档：`docs/superpowers/specs/2026-05-31-frontend-data-story-design.md`

---

## 约定

- 所有命令在项目根 `F:\claude-output\电商App用户路径与留存分析项目` 下运行；前端命令在 `web/` 下运行。
- 项目当前不是 git 仓库 → Task 0 执行 `git init`，之后每个 Task 末尾提交。
- 数字格式：用 `metrics.json` 内的值，不在前端重算口径。

---

### Task 0: 初始化 git + 脚手架 web/（Vite React TS + Tailwind）

**Files:**
- Create: `web/` (Vite 脚手架生成)
- Modify: `.gitignore`

- [ ] **Step 1: 初始化 git 仓库**

Run:
```bash
git init
git add -A
git commit -m "chore: snapshot before frontend work"
```
Expected: 创建仓库并提交现有文件。

- [ ] **Step 2: 用 Vite 脚手架生成 web/**

Run:
```bash
npm create vite@latest web -- --template react-ts
cd web && npm install
```
Expected: 生成 `web/`，`npm install` 成功。

- [ ] **Step 3: 安装依赖**

Run（在 `web/` 下）:
```bash
npm install framer-motion recharts
npm install -D tailwindcss@3 postcss autoprefixer vitest @testing-library/react @testing-library/jest-dom jsdom
npx tailwindcss init -p
```
Expected: 依赖装好，生成 `tailwind.config.js` 与 `postcss.config.js`。

- [ ] **Step 4: 配置 Tailwind content 与 Vitest**

修改 `web/tailwind.config.js`：
```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: { extend: {} },
  plugins: [],
};
```

修改 `web/vite.config.ts`：
```ts
/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: { environment: "jsdom", globals: true, setupFiles: "./src/test/setup.ts" },
});
```

创建 `web/src/test/setup.ts`：
```ts
import "@testing-library/jest-dom";
```

创建 `web/src/index.css`（替换默认内容）：
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

在 `web/src/main.tsx` 确保 `import "./index.css";` 存在。

- [ ] **Step 5: 加测试脚本**

在 `web/package.json` 的 `scripts` 加入：
```json
"test": "vitest run",
"test:watch": "vitest"
```

- [ ] **Step 6: 验证脚手架可构建**

Run（在 `web/` 下）:
```bash
npm run build
```
Expected: vite build 成功，生成 `web/dist/`。

- [ ] **Step 7: 忽略 web 构建产物并提交**

在根 `.gitignore` 末尾追加：
```
web/node_modules/
web/dist/
```
Run:
```bash
git add -A
git commit -m "chore(web): scaffold vite react-ts + tailwind + vitest"
```

---

### Task 1: Python 数据烘焙 export_web_data.py（TDD）

把指标 CSV + 质量报告 + insights 烘焙成 `web/src/data/metrics.json`。

**Files:**
- Create: `src/export_web_data.py`
- Test: `tests/test_export_web_data.py`

- [ ] **Step 1: 写失败测试**

创建 `tests/test_export_web_data.py`：
```python
from __future__ import annotations

import json

import pandas as pd

from src.export_web_data import build_web_payload


def test_payload_sections_match_source_csv(tmp_path):
    metrics_dir = tmp_path / "metrics"
    metrics_dir.mkdir()
    funnel = pd.DataFrame(
        [{"step": "view", "users": 10, "sessions": 12, "overall_rate": 1.0, "step_rate": 1.0}]
    )
    funnel.to_csv(metrics_dir / "funnel.csv", index=False)
    quality = {"rows": 100, "users": 10, "sessions": 12,
               "date_range": {"min": "2019-11-01", "max": "2019-11-16"}}
    (tmp_path / "data_quality_report.json").write_text(json.dumps(quality), encoding="utf-8")
    (tmp_path / "insights.md").write_text("# Key Insights\n\n- 结论一\n- 结论二\n", encoding="utf-8")

    payload = build_web_payload(metrics_dir=metrics_dir,
                                quality_path=tmp_path / "data_quality_report.json",
                                insights_path=tmp_path / "insights.md")

    assert payload["funnel"] == funnel.to_dict("records")
    assert payload["scope"]["users"] == 10
    assert payload["scope"]["date_range"] == {"min": "2019-11-01", "max": "2019-11-16"}
    assert payload["insights"] == ["结论一", "结论二"]
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python -m pytest tests/test_export_web_data.py -q -p no:cacheprovider`
Expected: FAIL（`ModuleNotFoundError: No module named 'src.export_web_data'`）。

- [ ] **Step 3: 实现 export_web_data.py**

创建 `src/export_web_data.py`：
```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import PROCESSED_DIR, REPORTS_DIR

WEB_DATA_PATH = Path(__file__).resolve().parents[1] / "web" / "src" / "data" / "metrics.json"
METRIC_FILES = [
    "daily_kpis", "funnel", "retention", "paths", "purchase_paths",
    "segments", "session_depth", "category", "price_band", "cart_abandonment",
]


def _read_insights(insights_path: Path) -> list[str]:
    if not insights_path.exists():
        return []
    return [
        line[2:].strip()
        for line in insights_path.read_text(encoding="utf-8").splitlines()
        if line.startswith("- ")
    ]


def build_web_payload(
    metrics_dir: Path = PROCESSED_DIR / "metrics",
    quality_path: Path = REPORTS_DIR / "data_quality_report.json",
    insights_path: Path = REPORTS_DIR / "insights.md",
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for name in METRIC_FILES:
        csv_path = metrics_dir / f"{name}.csv"
        if csv_path.exists():
            payload[name] = pd.read_csv(csv_path).to_dict("records")
        else:
            payload[name] = []
    quality = json.loads(quality_path.read_text(encoding="utf-8")) if quality_path.exists() else {}
    payload["scope"] = {
        "rows": quality.get("rows", 0),
        "users": quality.get("users", 0),
        "sessions": quality.get("sessions", 0),
        "date_range": quality.get("date_range", {}),
    }
    payload["insights"] = _read_insights(insights_path)
    return payload


def write_web_payload(path: Path = WEB_DATA_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_web_payload()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_web_payload()
    print(f"Wrote web data: {out}")
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python -m pytest tests/test_export_web_data.py -q -p no:cacheprovider`
Expected: PASS。

- [ ] **Step 5: 生成真实 metrics.json**

Run: `python -m src.export_web_data`
Expected: 打印 `Wrote web data: ...web/src/data/metrics.json`，文件存在且含 funnel/retention/scope/insights。

- [ ] **Step 6: 提交**

```bash
git add src/export_web_data.py tests/test_export_web_data.py web/src/data/metrics.json
git commit -m "feat(data): bake metrics.json for the web story page"
```

---

### Task 2: 视觉 tokens（theme.ts）

**Files:**
- Create: `web/src/theme.ts`

- [ ] **Step 1: 写 theme tokens**

创建 `web/src/theme.ts`：
```ts
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
```

- [ ] **Step 2: 提交**

```bash
git add web/src/theme.ts
git commit -m "feat(web): warm-luxe design tokens"
```

---

### Task 3: 格式化工具 lib/format.ts（TDD）

**Files:**
- Create: `web/src/lib/format.ts`
- Test: `web/src/lib/format.test.ts`

- [ ] **Step 1: 写失败测试**

创建 `web/src/lib/format.test.ts`：
```ts
import { describe, it, expect } from "vitest";
import { fmtInt, fmtPct, fmtMoney } from "./format";

describe("format", () => {
  it("formats integers with thousands separators", () => {
    expect(fmtInt(41944)).toBe("41,944");
  });
  it("formats percentages from a 0-1 ratio", () => {
    expect(fmtPct(0.181)).toBe("18.1%");
  });
  it("formats money compactly", () => {
    expect(fmtMoney(89124.16)).toBe("¥89,124");
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run（`web/`）: `npm run test -- format`
Expected: FAIL（找不到 `./format`）。

- [ ] **Step 3: 实现 format.ts**

创建 `web/src/lib/format.ts`：
```ts
export const fmtInt = (n: number): string => Math.round(n).toLocaleString("en-US");

export const fmtPct = (ratio: number, digits = 1): string =>
  `${(ratio * 100).toFixed(digits)}%`;

export const fmtMoney = (n: number): string => `¥${Math.round(n).toLocaleString("en-US")}`;
```

- [ ] **Step 4: 跑测试确认通过**

Run: `npm run test -- format`
Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add web/src/lib/format.ts web/src/lib/format.test.ts
git commit -m "feat(web): number/percent/money formatting helpers"
```

---

### Task 4: 数字滚动 hook lib/useCountUp.ts（TDD）

**Files:**
- Create: `web/src/lib/useCountUp.ts`
- Test: `web/src/lib/useCountUp.test.tsx`

- [ ] **Step 1: 写失败测试**

创建 `web/src/lib/useCountUp.test.tsx`：
```tsx
import { describe, it, expect } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { useCountUp } from "./useCountUp";

function Probe({ to }: { to: number }) {
  const value = useCountUp(to, true, 0);
  return <span data-testid="v">{Math.round(value)}</span>;
}

describe("useCountUp", () => {
  it("settles on the target value when active", async () => {
    render(<Probe to={165} />);
    await waitFor(() => expect(screen.getByTestId("v").textContent).toBe("165"));
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `npm run test -- useCountUp`
Expected: FAIL（找不到 `./useCountUp`）。

- [ ] **Step 3: 实现 useCountUp.ts**

创建 `web/src/lib/useCountUp.ts`：
```ts
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
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / durationMs);
      const eased = 1 - Math.pow(1 - t, 3); // easeOutCubic
      setValue(target * eased);
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [active, target, durationMs]);

  return value;
}
```

- [ ] **Step 4: 跑测试确认通过**

Run: `npm run test -- useCountUp`
Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add web/src/lib/useCountUp.ts web/src/lib/useCountUp.test.tsx
git commit -m "feat(web): useCountUp number animation hook"
```

---

### Task 5: 滚动进度 hook lib/useScrollProgress.ts

**Files:**
- Create: `web/src/lib/useScrollProgress.ts`

- [ ] **Step 1: 实现 hook**

创建 `web/src/lib/useScrollProgress.ts`：
```ts
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
```

- [ ] **Step 2: 验证类型可编译**

Run（`web/`）: `npx tsc --noEmit`
Expected: 无类型错误。

- [ ] **Step 3: 提交**

```bash
git add web/src/lib/useScrollProgress.ts
git commit -m "feat(web): scroll-progress hook for sticky charts"
```

---

### Task 6: KpiCard 组件（含 count-up，TDD 冒烟）

**Files:**
- Create: `web/src/components/KpiCard.tsx`
- Test: `web/src/components/KpiCard.test.tsx`

- [ ] **Step 1: 写失败测试**

创建 `web/src/components/KpiCard.test.tsx`：
```tsx
import { describe, it, expect } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { KpiCard } from "./KpiCard";

describe("KpiCard", () => {
  it("renders label and counts up to the formatted value", async () => {
    render(<KpiCard label="购买用户" value={165} format={(n) => String(Math.round(n))} active />);
    expect(screen.getByText("购买用户")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("165")).toBeInTheDocument());
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `npm run test -- KpiCard`
Expected: FAIL。

- [ ] **Step 3: 实现 KpiCard.tsx**

创建 `web/src/components/KpiCard.tsx`：
```tsx
import { theme } from "../theme";
import { useCountUp } from "../lib/useCountUp";

interface KpiCardProps {
  label: string;
  value: number;
  format: (n: number) => string;
  active: boolean;
}

export function KpiCard({ label, value, format, active }: KpiCardProps) {
  const animated = useCountUp(value, active, 1000);
  return (
    <div
      className="rounded-xl px-5 py-4"
      style={{
        background: theme.color.surface,
        border: `1px solid ${theme.color.border}`,
        borderLeft: `4px solid ${theme.color.teal}`,
        boxShadow: theme.shadow,
      }}
    >
      <div className="text-sm font-semibold" style={{ color: theme.color.muted }}>
        {label}
      </div>
      <div className="mt-1 text-3xl font-extrabold" style={{ color: theme.color.teal }}>
        {format(animated)}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: 跑测试确认通过**

Run: `npm run test -- KpiCard`
Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add web/src/components/KpiCard.tsx web/src/components/KpiCard.test.tsx
git commit -m "feat(web): KpiCard with count-up"
```

---

### Task 7: Section / Takeaway / ProgressRail 骨架组件

**Files:**
- Create: `web/src/components/Section.tsx`
- Create: `web/src/components/Takeaway.tsx`
- Create: `web/src/components/ProgressRail.tsx`

- [ ] **Step 1: 实现 Section.tsx（滚动入场 + 上报可见状态）**

创建 `web/src/components/Section.tsx`：
```tsx
import { ReactNode, useRef } from "react";
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
  if (inView) onActive?.(id);
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
```

- [ ] **Step 2: 实现 Takeaway.tsx**

创建 `web/src/components/Takeaway.tsx`：
```tsx
import { theme } from "../theme";

export function Takeaway({ children }: { children: React.ReactNode }) {
  return (
    <p
      className="mt-6 text-lg leading-relaxed"
      style={{ color: theme.color.ink, borderLeft: `3px solid ${theme.color.gold}`, paddingLeft: 14 }}
    >
      {children}
    </p>
  );
}
```

- [ ] **Step 3: 实现 ProgressRail.tsx**

创建 `web/src/components/ProgressRail.tsx`：
```tsx
import { theme } from "../theme";

interface ProgressRailProps {
  sections: { id: string; label: string }[];
  active: string;
}

export function ProgressRail({ sections, active }: ProgressRailProps) {
  return (
    <nav className="fixed left-6 top-1/2 -translate-y-1/2 z-50 hidden lg:flex flex-col gap-4">
      {sections.map((s) => {
        const on = s.id === active;
        return (
          <a key={s.id} href={`#${s.id}`} className="flex items-center gap-3 group">
            <span
              className="block rounded-full transition-all"
              style={{
                width: on ? 12 : 9,
                height: on ? 12 : 9,
                background: on ? theme.color.teal : "#cbbfa6",
                boxShadow: on ? `0 0 0 4px rgba(15,94,87,.18)` : "none",
              }}
            />
            <span
              className="text-sm transition-opacity"
              style={{ color: theme.color.muted, opacity: on ? 1 : 0.55 }}
            >
              {s.label}
            </span>
          </a>
        );
      })}
    </nav>
  );
}
```

- [ ] **Step 4: 验证编译**

Run: `npx tsc --noEmit`
Expected: 无错误。

- [ ] **Step 5: 提交**

```bash
git add web/src/components/Section.tsx web/src/components/Takeaway.tsx web/src/components/ProgressRail.tsx
git commit -m "feat(web): Section/Takeaway/ProgressRail skeleton"
```

---

### Task 8: TrendChart（Recharts 折线，趋势）

**Files:**
- Create: `web/src/components/charts/TrendChart.tsx`

- [ ] **Step 1: 实现 TrendChart.tsx**

创建 `web/src/components/charts/TrendChart.tsx`：
```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { theme } from "../../theme";

interface DailyRow { event_date: string; dau: number; cart_adds: number; purchases: number; }

export function TrendChart({ data, active }: { data: DailyRow[]; active: boolean }) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
        <CartesianGrid stroke={theme.color.border} vertical={false} />
        <XAxis dataKey="event_date" tick={{ fill: theme.color.muted, fontSize: 12 }} />
        <YAxis tick={{ fill: theme.color.muted, fontSize: 12 }} />
        <Tooltip />
        <Line type="monotone" dataKey="dau" stroke={theme.series[0]} strokeWidth={2.5}
              dot={false} isAnimationActive={active} animationDuration={1100} />
        <Line type="monotone" dataKey="cart_adds" stroke={theme.series[1]} strokeWidth={2.5}
              dot={false} isAnimationActive={active} animationDuration={1100} />
        <Line type="monotone" dataKey="purchases" stroke={theme.series[2]} strokeWidth={2.5}
              dot={false} isAnimationActive={active} animationDuration={1100} />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

- [ ] **Step 2: 编译验证并提交**

Run: `npx tsc --noEmit`
```bash
git add web/src/components/charts/TrendChart.tsx
git commit -m "feat(web): trend line chart"
```

---

### Task 9: FunnelSticky（自定义 SVG 漏斗，钉图逐级点亮，TDD 冒烟）

**Files:**
- Create: `web/src/components/charts/FunnelSticky.tsx`
- Test: `web/src/components/charts/FunnelSticky.test.tsx`

- [ ] **Step 1: 写失败测试**

创建 `web/src/components/charts/FunnelSticky.test.tsx`：
```tsx
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { FunnelSticky } from "./FunnelSticky";

const rows = [
  { step: "view", users: 2536, overall_rate: 1, step_rate: 1 },
  { step: "cart", users: 459, overall_rate: 0.181, step_rate: 0.181 },
  { step: "purchase", users: 165, overall_rate: 0.0651, step_rate: 0.3595 },
];

describe("FunnelSticky", () => {
  it("renders every funnel step label and user count", () => {
    render(<FunnelSticky data={rows} progress={1} />);
    expect(screen.getByText(/view/i)).toBeInTheDocument();
    expect(screen.getByText("2,536")).toBeInTheDocument();
    expect(screen.getByText("165")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `npm run test -- FunnelSticky`
Expected: FAIL。

- [ ] **Step 3: 实现 FunnelSticky.tsx**

创建 `web/src/components/charts/FunnelSticky.tsx`：
```tsx
import { theme } from "../../theme";
import { fmtInt, fmtPct } from "../../lib/format";

interface FunnelRow { step: string; users: number; overall_rate: number; step_rate: number; }

const STEP_LABEL: Record<string, string> = { view: "浏览 View", cart: "加购 Cart", purchase: "购买 Purchase" };

// progress: 0→1，决定点亮到第几级（0.. data.length）。
export function FunnelSticky({ data, progress }: { data: FunnelRow[]; progress: number }) {
  const top = data[0]?.users || 1;
  const lit = progress * data.length;
  return (
    <div className="flex flex-col gap-3">
      {data.map((row, i) => {
        const widthPct = Math.max(8, (row.users / top) * 100);
        const on = lit >= i + 0.5;
        return (
          <div key={row.step} className="flex items-center gap-4">
            <div className="w-28 text-right text-sm font-semibold" style={{ color: theme.color.muted }}>
              {STEP_LABEL[row.step] ?? row.step}
            </div>
            <div className="flex-1 h-16 relative">
              <div
                className="h-full rounded-lg flex items-center px-4 transition-all duration-700"
                style={{
                  width: `${widthPct}%`,
                  background: on ? theme.series[i % theme.series.length] : theme.color.border,
                  opacity: on ? 1 : 0.45,
                  boxShadow: on ? theme.shadow : "none",
                }}
              >
                <span className="font-extrabold text-white">{fmtInt(row.users)}</span>
                <span className="ml-3 text-white/85 text-sm">{fmtPct(row.overall_rate)} 整体</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 4: 跑测试确认通过**

Run: `npm run test -- FunnelSticky`
Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add web/src/components/charts/FunnelSticky.tsx web/src/components/charts/FunnelSticky.test.tsx
git commit -m "feat(web): sticky funnel that lights up by scroll progress"
```

---

### Task 10: RetentionHeatmap（自定义 SVG 热力图，钉图逐列点亮）

**Files:**
- Create: `web/src/components/charts/RetentionHeatmap.tsx`

- [ ] **Step 1: 实现 RetentionHeatmap.tsx**

创建 `web/src/components/charts/RetentionHeatmap.tsx`：
```tsx
import { theme } from "../../theme";
import { fmtPct } from "../../lib/format";

interface RetRow { cohort_date: string; days_since_first: number; retention_rate: number; }

const DAYS = [1, 3, 7];

function shade(rate: number): string {
  // 在 canvas→teal 之间插值
  const t = Math.min(1, rate / 0.3);
  const mix = (a: number, b: number) => Math.round(a + (b - a) * t);
  const c1 = [242, 240, 232]; // #f2f0e8
  const c2 = [15, 94, 87]; // teal
  return `rgb(${mix(c1[0], c2[0])},${mix(c1[1], c2[1])},${mix(c1[2], c2[2])})`;
}

// progress 0→1 控制点亮到第几列（D1→D3→D7）。
export function RetentionHeatmap({ data, progress }: { data: RetRow[]; progress: number }) {
  const cohorts = Array.from(new Set(data.map((d) => d.cohort_date))).sort();
  const litCols = progress * DAYS.length;
  const lookup = new Map(data.map((d) => [`${d.cohort_date}|${d.days_since_first}`, d.retention_rate]));
  return (
    <div className="overflow-x-auto">
      <div className="grid gap-1" style={{ gridTemplateColumns: `120px repeat(${DAYS.length}, 64px)` }}>
        <div />
        {DAYS.map((d) => (
          <div key={d} className="text-center text-sm font-semibold" style={{ color: theme.color.muted }}>D{d}</div>
        ))}
        {cohorts.map((c) => (
          <FragmentRow key={c} cohort={c} lookup={lookup} litCols={litCols} />
        ))}
      </div>
    </div>
  );
}

function FragmentRow({ cohort, lookup, litCols }: {
  cohort: string; lookup: Map<string, number>; litCols: number;
}) {
  return (
    <>
      <div className="text-xs flex items-center" style={{ color: theme.color.muted }}>{cohort.slice(5)}</div>
      {DAYS.map((d, i) => {
        const rate = lookup.get(`${cohort}|${d}`) ?? 0;
        const on = litCols >= i + 0.5;
        return (
          <div key={d} className="h-12 rounded flex items-center justify-center text-xs transition-all duration-500"
               style={{ background: on ? shade(rate) : theme.color.border,
                        color: rate > 0.15 ? "#fff" : theme.color.ink, opacity: on ? 1 : 0.4 }}>
            {on ? fmtPct(rate) : ""}
          </div>
        );
      })}
    </>
  );
}
```

- [ ] **Step 2: 编译验证并提交**

Run: `npx tsc --noEmit`
```bash
git add web/src/components/charts/RetentionHeatmap.tsx
git commit -m "feat(web): sticky retention heatmap lit by columns"
```

---

### Task 11: 其余标准图（Recharts）

**Files:**
- Create: `web/src/components/charts/PriceBandChart.tsx`
- Create: `web/src/components/charts/PathBars.tsx`
- Create: `web/src/components/charts/PurchasePathCompare.tsx`
- Create: `web/src/components/charts/SegmentDonut.tsx`
- Create: `web/src/components/charts/SessionDepthChart.tsx`
- Create: `web/src/components/charts/CategoryBars.tsx`

- [ ] **Step 1: 实现 PriceBandChart.tsx**

```tsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { theme } from "../../theme";

export function PriceBandChart({ data, active }: { data: any[]; active: boolean }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data}>
        <CartesianGrid stroke={theme.color.border} vertical={false} />
        <XAxis dataKey="price_band" tick={{ fill: theme.color.muted, fontSize: 12 }} />
        <YAxis tick={{ fill: theme.color.muted, fontSize: 12 }} />
        <Tooltip /><Legend />
        <Bar dataKey="cart_rate" fill={theme.series[0]} isAnimationActive={active} />
        <Bar dataKey="purchase_rate" fill={theme.series[1]} isAnimationActive={active} />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

- [ ] **Step 2: 实现 PathBars.tsx**

```tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { theme } from "../../theme";

export function PathBars({ data, active }: { data: { path: string; sessions: number }[]; active: boolean }) {
  const sorted = [...data].sort((a, b) => a.sessions - b.sessions);
  return (
    <ResponsiveContainer width="100%" height={Math.max(260, sorted.length * 34)}>
      <BarChart layout="vertical" data={sorted} margin={{ left: 40 }}>
        <XAxis type="number" tick={{ fill: theme.color.muted, fontSize: 12 }} />
        <YAxis type="category" dataKey="path" width={220} tick={{ fill: theme.color.muted, fontSize: 11 }} />
        <Tooltip />
        <Bar dataKey="sessions" fill={theme.series[0]} radius={[0, 5, 5, 0]} isAnimationActive={active} />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

- [ ] **Step 3: 实现 PurchasePathCompare.tsx**

```tsx
import { theme } from "../../theme";

interface Row { session_type: string; path: string; sessions: number; }

export function PurchasePathCompare({ data }: { data: Row[] }) {
  const groups = ["Purchased", "No Purchase"];
  return (
    <div className="grid md:grid-cols-2 gap-6">
      {groups.map((g) => {
        const rows = data.filter((d) => d.session_type === g).slice(0, 6);
        const max = Math.max(1, ...rows.map((r) => r.sessions));
        return (
          <div key={g}>
            <h4 className="font-semibold mb-3" style={{ color: theme.color.ink }}>{g}</h4>
            {rows.map((r) => (
              <div key={r.path} className="mb-2">
                <div className="text-xs mb-1" style={{ color: theme.color.muted }}>{r.path}</div>
                <div className="h-3 rounded" style={{
                  width: `${(r.sessions / max) * 100}%`,
                  background: g === "Purchased" ? theme.series[0] : theme.series[2],
                }} />
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 4: 实现 SegmentDonut.tsx**

```tsx
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { theme } from "../../theme";

export function SegmentDonut({ data, active }: { data: { segment: string; users: number }[]; active: boolean }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie data={data} dataKey="users" nameKey="segment" innerRadius={70} outerRadius={110}
             isAnimationActive={active} label>
          {data.map((_, i) => <Cell key={i} fill={theme.series[i % theme.series.length]} />)}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}
```

- [ ] **Step 5: 实现 SessionDepthChart.tsx**

```tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { theme } from "../../theme";

export function SessionDepthChart({ data, active }: { data: any[]; active: boolean }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data}>
        <XAxis dataKey="session_type" tick={{ fill: theme.color.muted, fontSize: 12 }} />
        <YAxis tick={{ fill: theme.color.muted, fontSize: 12 }} />
        <Tooltip /><Legend />
        <Bar dataKey="avg_events_per_session" fill={theme.series[0]} isAnimationActive={active} />
        <Bar dataKey="avg_products_per_session" fill={theme.series[1]} isAnimationActive={active} />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

- [ ] **Step 6: 实现 CategoryBars.tsx**

```tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { theme } from "../../theme";

export function CategoryBars({ data, active }: { data: any[]; active: boolean }) {
  const sorted = [...data].sort((a, b) => a.gmv - b.gmv);
  return (
    <ResponsiveContainer width="100%" height={Math.max(260, sorted.length * 32)}>
      <BarChart layout="vertical" data={sorted} margin={{ left: 60 }}>
        <XAxis type="number" tick={{ fill: theme.color.muted, fontSize: 12 }} />
        <YAxis type="category" dataKey="category_code" width={180} tick={{ fill: theme.color.muted, fontSize: 11 }} />
        <Tooltip />
        <Bar dataKey="gmv" fill={theme.series[1]} radius={[0, 5, 5, 0]} isAnimationActive={active} />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

- [ ] **Step 7: 编译验证并提交**

Run: `npx tsc --noEmit`
```bash
git add web/src/components/charts/
git commit -m "feat(web): standard recharts charts (price band/paths/segments/category/session depth)"
```

---

### Task 12: 章节组件（sections）

**Files:**
- Create: `web/src/sections/Hero.tsx`
- Create: `web/src/sections/Overview.tsx`
- Create: `web/src/sections/Conversion.tsx`
- Create: `web/src/sections/Retention.tsx`
- Create: `web/src/sections/UserPath.tsx`
- Create: `web/src/sections/Segments.tsx`
- Create: `web/src/sections/Insights.tsx`

- [ ] **Step 1: 定义数据类型 web/src/lib/data.ts**

```ts
import raw from "../data/metrics.json";

export interface Metrics {
  daily_kpis: any[]; funnel: any[]; retention: any[]; paths: any[];
  purchase_paths: any[]; segments: any[]; session_depth: any[];
  category: any[]; price_band: any[]; cart_abandonment: any[];
  scope: { rows: number; users: number; sessions: number; date_range: { min?: string; max?: string } };
  insights: string[];
}

export const metrics = raw as unknown as Metrics;
```

- [ ] **Step 2: 实现 Hero.tsx**

```tsx
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
```

- [ ] **Step 3: 实现 Overview.tsx**

```tsx
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
```

- [ ] **Step 4: 实现 Conversion.tsx（钉图）**

```tsx
import { useRef } from "react";
import { useMotionValueEvent } from "framer-motion";
import { useState } from "react";
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
  useMotionValueEvent(progress, "change", (v) => { setP(v); if (v > 0.05 && v < 0.95) onActive("conversion"); });
  const ca = metrics.cart_abandonment[0] ?? { abandonment_rate: 0 };
  return (
    <section ref={ref} id="conversion" className="relative" style={{ height: "220vh" }}>
      <div className="sticky top-0 min-h-screen flex flex-col justify-center px-8 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold mb-8" style={{ color: theme.color.teal }}>转化漏斗</h2>
        <FunnelSticky data={metrics.funnel} progress={p} />
        <div className="mt-10"><PriceBandChart data={metrics.price_band} active={p > 0.6} /></div>
        <Takeaway>加购放弃率约 {fmtPct(ca.abandonment_rate)}；加购未买用户是购物车召回与价格提醒的首选对象。</Takeaway>
      </div>
    </section>
  );
}
```

- [ ] **Step 5: 实现 Retention.tsx（钉图）**

```tsx
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
  useMotionValueEvent(progress, "change", (v) => { setP(v); if (v > 0.05 && v < 0.95) onActive("retention"); });
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
```

- [ ] **Step 6: 实现 UserPath.tsx**

```tsx
import { Section } from "../components/Section";
import { PathBars } from "../components/charts/PathBars";
import { PurchasePathCompare } from "../components/charts/PurchasePathCompare";
import { Takeaway } from "../components/Takeaway";
import { metrics } from "../lib/data";

export function UserPath({ onActive }: { onActive: (id: string) => void }) {
  return (
    <Section id="userpath" title="用户路径" onActive={onActive}>
      {(active) => (
        <>
          <PathBars data={metrics.paths} active={active} />
          <div className="mt-10"><PurchasePathCompare data={metrics.purchase_paths} /></div>
          <Takeaway>多数 session 停在浏览阶段；购买 session 的行为序列更长、更聚焦。</Takeaway>
        </>
      )}
    </Section>
  );
}
```

- [ ] **Step 7: 实现 Segments.tsx**

```tsx
import { Section } from "../components/Section";
import { SegmentDonut } from "../components/charts/SegmentDonut";
import { SessionDepthChart } from "../components/charts/SessionDepthChart";
import { CategoryBars } from "../components/charts/CategoryBars";
import { Takeaway } from "../components/Takeaway";
import { metrics } from "../lib/data";

export function Segments({ onActive }: { onActive: (id: string) => void }) {
  return (
    <Section id="segments" title="用户分层与品类" onActive={onActive}>
      {(active) => (
        <>
          <div className="grid md:grid-cols-2 gap-8">
            <SegmentDonut data={metrics.segments} active={active} />
            <SessionDepthChart data={metrics.session_depth} active={active} />
          </div>
          <div className="mt-10"><CategoryBars data={metrics.category} active={active} /></div>
          <Takeaway>最大群体是 Browsers Only；购买/复购用户是精细化运营与资源倾斜的重点。</Takeaway>
        </>
      )}
    </Section>
  );
}
```

- [ ] **Step 8: 实现 Insights.tsx**

```tsx
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
```

- [ ] **Step 9: 编译验证并提交**

Run: `npx tsc --noEmit`
```bash
git add web/src/lib/data.ts web/src/sections/
git commit -m "feat(web): all story sections (hero/overview/conversion/retention/path/segments/insights)"
```

---

### Task 13: App.tsx 组装 + 全局背景

**Files:**
- Modify: `web/src/App.tsx`
- Modify: `web/src/index.css`

- [ ] **Step 1: 全局背景**

在 `web/src/index.css` 追加：
```css
:root { color-scheme: light; }
body {
  background: linear-gradient(180deg, #faf6ef 0%, #f1f5f0 100%);
  font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", "Segoe UI", sans-serif;
}
html { scroll-behavior: smooth; }
```

- [ ] **Step 2: 组装 App.tsx**

替换 `web/src/App.tsx`：
```tsx
import { useState } from "react";
import { ProgressRail } from "./components/ProgressRail";
import { Hero } from "./sections/Hero";
import { Overview } from "./sections/Overview";
import { Conversion } from "./sections/Conversion";
import { Retention } from "./sections/Retention";
import { UserPath } from "./sections/UserPath";
import { Segments } from "./sections/Segments";
import { Insights } from "./sections/Insights";

const RAIL = [
  { id: "overview", label: "整体" },
  { id: "conversion", label: "转化" },
  { id: "retention", label: "留存" },
  { id: "userpath", label: "路径" },
  { id: "segments", label: "分层" },
  { id: "insights", label: "洞察" },
];

export default function App() {
  const [active, setActive] = useState("overview");
  return (
    <>
      <ProgressRail sections={RAIL} active={active} />
      <Hero />
      <Overview onActive={setActive} />
      <Conversion onActive={setActive} />
      <Retention onActive={setActive} />
      <UserPath onActive={setActive} />
      <Segments onActive={setActive} />
      <Insights onActive={setActive} />
    </>
  );
}
```

- [ ] **Step 3: 跑前端测试 + 构建**

Run（`web/`）:
```bash
npm run test
npm run build
```
Expected: 测试全过；vite build 成功。

- [ ] **Step 4: 本地预览人工确认**

Run: `npm run dev`，浏览器打开提示的 URL。
确认：进度轴高亮跟随、KPI 数字滚动、趋势线生长、漏斗随滚动逐级点亮、留存热力图逐列点亮、洞察卡逐条淡入。

- [ ] **Step 5: 提交**

```bash
git add web/src/App.tsx web/src/index.css
git commit -m "feat(web): assemble scrollytelling app with progress rail"
```

---

### Task 14: 管道接入 + 文档 + 审计放行

**Files:**
- Modify: `run_pipeline.ps1`
- Modify: `README.md`
- Modify: `src/project_audit.py`（如需放行 `web/`）

- [ ] **Step 1: pipeline 增加数据烘焙**

在 `run_pipeline.ps1` 的 `Invoke-PythonModule -Arguments @("-m", "src.export_outputs")` 之后追加一行：
```powershell
Invoke-PythonModule -Arguments @("-m", "src.export_web_data")
```

- [ ] **Step 2: 确认 audit 不误报 web/**

Run: `python -c "import json; d=json.load(open('reports/project_audit_report.json',encoding='utf-8'))"`（先 `$env:PYTHONDONTWRITEBYTECODE=1; python -m src.project_audit`）。
若 `web/`、`docs/` 被标记为应删除：在 `src/project_audit.py` 的忽略/允许列表中加入 `web`、`docs`（按其现有实现的目录白名单字段添加）。
Expected: 审计 `status: pass`。

- [ ] **Step 3: README 增加展示页说明**

在 README「Dashboard 页面」之后新增一节：
```markdown
## 数据故事页（独立前端）

`web/` 是一个 Vite + React 的只读展示页，读取由 `python -m src.export_web_data` 烘焙的 `web/src/data/metrics.json`（与 Streamlit 用同一套指标）。

启动：
```bash
cd web && npm install && npm run dev
```
```

- [ ] **Step 4: 全量回归 + 提交**

Run（根目录）: `python -m pytest -q -p no:cacheprovider`
Expected: 全过（含新增 `test_export_web_data.py`）。
```bash
git add run_pipeline.ps1 README.md src/project_audit.py
git commit -m "chore: wire web data bake into pipeline + docs + audit"
```

---

## Self-Review

- **Spec 覆盖**：定位/边界(Task 0,14)、数据管道+一致性(Task 1)、tokens(Task 2)、四层连贯性—叙事(Section/钉图 Task 7,9,10,12)/数值一致(单一 metrics.json Task 1,12-1)/过渡(useCountUp Task 4,6 + 图表动画)/体系统一(theme Task 2 全组件复用)、页面结构七章(Task 12)、图表选型 Recharts+自定义 SVG(Task 8-11)、验证(build+vitest+pytest Task 1,3,4,6,9,13,14)。全部有对应任务。
- **占位符扫描**：无 TBD/TODO；每个代码步骤给出完整代码。
- **类型一致**：`metrics`(data.ts) 字段与各 section 使用一致；`Section` 的 `children:(active)=>ReactNode` 与 Overview/UserPath/Segments/Insights 用法一致；`useScrollProgress` 返回 MotionValue，Conversion/Retention 用 `useMotionValueEvent` 取值一致；`FunnelSticky`/`RetentionHeatmap` 的 `progress:number` 与传入 `p` 一致。

> 已知简化：标准图组件入参用 `any[]`（只读展示、字段来自固定 JSON），如需更严类型可在后续迭代为各 CSV 定义 interface。
