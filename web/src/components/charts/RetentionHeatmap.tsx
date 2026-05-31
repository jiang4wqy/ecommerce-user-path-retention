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
          <div key={d} className="text-center text-sm font-semibold" style={{ color: theme.color.muted }}>
            D{d}
          </div>
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
