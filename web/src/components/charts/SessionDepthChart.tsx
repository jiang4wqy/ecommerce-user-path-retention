import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { theme } from "../../theme";

interface SessionDepthRow {
  session_type: string;
  avg_events_per_session: number;
  avg_products_per_session: number;
}

export function SessionDepthChart({ data, active }: { data: SessionDepthRow[]; active: boolean }) {
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
