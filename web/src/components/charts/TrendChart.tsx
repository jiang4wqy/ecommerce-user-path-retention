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
