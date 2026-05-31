import { theme } from "../../theme";

interface Row { session_type: string; path: string; sessions: number; }

export function PurchasePathCompare({ data }: { data: Row[] }) {
  const groups = ["Purchased", "No Purchase"];
  return (
    <div className="grid md:grid-cols-2 gap-6">
      {groups.map((g) => {
        const rows = data.filter((d) => d.session_type === g).slice(0, 6);
        const max = Math.max(1, ...rows.map((r) => r.sessions));
        return (
          <div key={g}>
            <h4 className="font-semibold mb-3" style={{ color: theme.color.ink }}>{g}</h4>
            {rows.map((r) => (
              <div key={r.path} className="mb-2">
                <div className="text-xs mb-1" style={{ color: theme.color.muted }}>{r.path}</div>
                <div className="h-3 rounded" style={{
                  width: `${(r.sessions / max) * 100}%`,
                  background: g === "Purchased" ? theme.series[0] : theme.series[2],
                }} />
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
}
