import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { theme } from "../../theme";

interface PriceBandRow { price_band: string; cart_rate: number; purchase_rate: number; }

export function PriceBandChart({ data, active }: { data: PriceBandRow[]; active: boolean }) {
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
