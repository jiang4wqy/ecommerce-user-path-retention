import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { FunnelSticky } from "./FunnelSticky";

const rows = [
  { step: "view", users: 2536, overall_rate: 1, step_rate: 1 },
  { step: "cart", users: 459, overall_rate: 0.181, step_rate: 0.181 },
  { step: "purchase", users: 165, overall_rate: 0.0651, step_rate: 0.3595 },
];

describe("FunnelSticky", () => {
  it("renders every funnel step label and user count", () => {
    render(<FunnelSticky data={rows} progress={1} />);
    expect(screen.getByText(/view/i)).toBeInTheDocument();
    expect(screen.getByText("2,536")).toBeInTheDocument();
    expect(screen.getByText("165")).toBeInTheDocument();
  });
});
