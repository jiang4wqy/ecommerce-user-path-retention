import { theme } from "../theme";

interface ProgressRailProps {
  sections: { id: string; label: string }[];
  active: string;
}

export function ProgressRail({ sections, active }: ProgressRailProps) {
  return (
    <nav className="fixed left-6 top-1/2 -translate-y-1/2 z-50 hidden lg:flex flex-col gap-4">
      {sections.map((s) => {
        const on = s.id === active;
        return (
          <a key={s.id} href={`#${s.id}`} className="flex items-center gap-3 group">
            <span
              className="block rounded-full transition-all"
              style={{
                width: on ? 12 : 9,
                height: on ? 12 : 9,
                background: on ? theme.color.teal : "#cbbfa6",
                boxShadow: on ? `0 0 0 4px rgba(15,94,87,.18)` : "none",
              }}
            />
            <span
              className="text-sm transition-opacity"
              style={{ color: theme.color.muted, opacity: on ? 1 : 0.55 }}
            >
              {s.label}
            </span>
          </a>
        );
      })}
    </nav>
  );
}
