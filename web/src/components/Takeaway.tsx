import type { ReactNode } from "react";
import { theme } from "../theme";

export function Takeaway({ children }: { children: ReactNode }) {
  return (
    <p
      className="mt-6 text-lg leading-relaxed"
      style={{ color: theme.color.ink, borderLeft: `3px solid ${theme.color.gold}`, paddingLeft: 14 }}
    >
      {children}
    </p>
  );
}
