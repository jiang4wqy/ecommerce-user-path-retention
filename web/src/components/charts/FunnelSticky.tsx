import { theme } from "../../theme";
import { fmtInt, fmtPct } from "../../lib/format";

interface FunnelRow { step: string; users: number; overall_rate: number; step_rate: number; }

const STEP_LABEL: Record<string, string> = {
  view: "浏览 View",
  cart: "加购 Cart",
  purchase: "购买 Purchase",
};

// progress: 0→1，决定点亮到第几级。
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
