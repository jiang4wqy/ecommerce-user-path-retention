import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { theme } from "../../theme";

interface CategoryRow { category_code: string; gmv: number; }

export function CategoryBars({ data, active }: { data: CategoryRow[]; active: boolean }) {
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
