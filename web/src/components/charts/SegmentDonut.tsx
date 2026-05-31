import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { theme } from "../../theme";

interface SegmentRow { segment: string; users: number; }

export function SegmentDonut({ data, active }: { data: SegmentRow[]; active: boolean }) {
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
