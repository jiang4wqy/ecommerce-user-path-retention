import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { theme } from "../../theme";

interface PathRow { path: string; sessions: number; }

export function PathBars({ data, active }: { data: PathRow[]; active: boolean }) {
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
