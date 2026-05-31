import { describe, it, expect } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { KpiCard } from "./KpiCard";

describe("KpiCard", () => {
  it("renders label and counts up to the formatted value", async () => {
    render(<KpiCard label="购买用户" value={165} format={(n) => String(Math.round(n))} active />);
    expect(screen.getByText("购买用户")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("165")).toBeInTheDocument(), { timeout: 2500 });
  });
});
