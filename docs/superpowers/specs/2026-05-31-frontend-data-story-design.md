# 前端数据故事页 — 设计文档

日期：2026-05-31
状态：已与用户确认，待转实现计划

## 1. 背景与目标

现有项目用 Streamlit 做了一个交互式分析工作台。本设计在其之上**新增一个独立的只读「数据故事」展示页**：读取同一套已算好的指标，做成有动画、有叙事、视觉统一的高级展示页，用于作品集/演示。

- 不替换 Streamlit 工作台，两者**并存**。
- 数据来自同一套指标，保证数字一致。
- 强调四层「数据连贯性」：叙事连贯（scrollytelling）、数值一致与互引、视觉过渡连贯、跨板块视觉体系统一。

### 非目标（YAGNI）
- 无实时筛选、无后端、无登录。
- 不做复杂移动端适配（桌面优先 + 合理自适应即可）。
- 除中文外不做多语言。
- 不替换或改动现有 Streamlit / Python 分析层逻辑（仅新增数据导出脚本）。

## 2. 关键决策（已确认）

| 维度 | 决定 |
|---|---|
| 形态 | 独立前端，与 Streamlit 并存 |
| 交互 | 只读展示型（读烘焙好的 JSON，无客户端筛选/重算） |
| 配色 | 暖调轻奢（Warm Luxe）：松绿 + 金 + 暖中性 |
| 布局 | A 长卷竖滚 + 左侧进度轴为骨架；漏斗、留存两个板块用 B「钉图叙事」点睛 |
| 技术栈 | Vite + React + Tailwind + Framer Motion |
| 图表 | 标准图用 Recharts；漏斗/留存钉图用自定义 SVG + Framer Motion |

## 3. 项目结构

新增 `web/` 子目录，不改动 Python 分析层：

```
web/
  index.html  vite.config.ts  package.json  tailwind.config.js  tsconfig.json
  src/
    main.tsx  App.tsx
    theme.ts                 # 暖调轻奢 design tokens（唯一视觉来源）
    data/metrics.json        # 由 Python 烘焙，前端唯一数据来源
    lib/
      format.ts              # 统一数字/百分比/货币格式化
      useCountUp.ts          # 数字滚动增长 hook
      useScrollProgress.ts   # 钉图滚动进度
    components/
      ProgressRail.tsx       # 左侧进度轴
      Section.tsx            # 标准板块容器（whileInView 入场）
      KpiCard.tsx            # 带 count-up 的 KPI 卡
      Takeaway.tsx           # 板块结论句
      charts/
        TrendChart.tsx  FunnelSticky.tsx  RetentionHeatmap.tsx
        PriceBandChart.tsx  PathBars.tsx  PurchasePathCompare.tsx
        SegmentDonut.tsx  SessionDepthChart.tsx  CategoryBars.tsx
    sections/
      Hero.tsx  Overview.tsx  Conversion.tsx  Retention.tsx
      UserPath.tsx  Segments.tsx  Insights.tsx
```

## 4. 数据管道（保证数值一致）

新增 `src/export_web_data.py`，纳入 `run_pipeline.ps1`：
- 读取 `data/processed/metrics/*.csv` 与 `reports/insights.md`。
- 写出 `web/src/data/metrics.json`（前端唯一数据来源）。
- JSON 形态：每个板块一个键（`daily_kpis`、`funnel`、`retention`、`paths`、`purchase_paths`、`segments`、`session_depth`、`category`、`price_band`、`cart_abandonment`、`insights`），值为记录数组 + 必要的汇总（如样本口径：事件数/用户数/会话数/日期范围）。

验证：新增 pytest 断言 `metrics.json` 与对应 CSV 数值一致（与已有的 SQL↔pandas 一致性测试同思路，防 drift）。

## 5. 页面结构与叙事

单页竖向滚动，左侧进度轴标记章节并高亮当前位置。

| 章节 | 形式 | 关键动画 |
|---|---|---|
| Hero | 全屏开场 | 标题/副标题入场；3 个核心数字 count-up |
| Overview | A 标准板块 | KPI 卡数字滚动增长；趋势线左→右生长 |
| Conversion | **B 钉图** | 漏斗钉住，滚动逐级点亮 view 2,536 → cart 18.1% → purchase 6.5%；下接价格带 + 加购放弃率 64% |
| Retention | **B 钉图** | cohort 热力图钉住，滚动按 D1→D3→D7 逐列点亮；留存 13.5% → 6.2% |
| User Path | A 标准板块 | Top 路径条形依次展开；购买 vs 未购买对比 |
| Segments | A 标准板块 | 环形图扇区生长；session 深度 / 品类条形 |
| Insights | A 收尾 | 结论卡逐条淡入，呼应前面各板块数字 |

每个 A 板块统一结构：章节标题 → 主图 → 一句 takeaway，上一段结论引出下一段。

## 6. 视觉体系（theme.ts，全站唯一来源）

- 颜色：canvas `#faf6ef` / surface `#fffdf8` / ink `#2b2117` / muted `#7a6a52` / 主色松绿 `#0f5e57` / 金 `#c79a3a` / 陶土 `#b06a3c` / 边框 `#e6dcc8`。
- 图表色序、圆角、阴影、间距尺度、动画缓动曲线全部 token 化。
- 字体：Microsoft YaHei / PingFang SC / Noto Sans CJK SC，标题加大字重。

## 7. 动画体系（对应四层连贯性）

- **叙事连贯**：`Section` 用 Framer Motion `whileInView` 入场；`ProgressRail` 用 `useScroll`/IntersectionObserver 跟踪当前章节；Conversion/Retention 用 sticky 容器 + 滚动进度（`useScrollProgress`）驱动图表分步状态。
- **数值一致互引**：单一 `metrics.json` + 统一 `format.ts`；漏斗顶部用户数 = Overview 总用户数；hover 品类时联动高亮相关指标。
- **视觉过渡连贯**：`useCountUp` 数字滚动；路径/柱用 `pathLength`/scale 生长；统一 easing，无硬跳变。
- **视觉体系统一**：见第 6 节 tokens，全部组件复用。

## 8. 图表选型

- 标准图（趋势线、条形、环形、热力图）：Recharts（React 友好、自带动画）。
- 两个钉图主角（漏斗、留存）：自定义 SVG + Framer Motion，以完全控制逐级点亮/变形。
- 控制库数量，不再引入额外图表库。

## 9. 验证方式

- `npm run build`（vite build）通过。
- 关键组件 Vitest + React Testing Library 冒烟渲染（Hero / KpiCard / FunnelSticky）。
- Python 端 `metrics.json` ↔ CSV 一致性 pytest。
- 浏览器实跑确认滚动 / 动画 / 钉图行为。

## 10. 开放问题

无（关键决策均已确认）。
