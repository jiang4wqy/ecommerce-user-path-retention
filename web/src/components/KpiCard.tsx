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
