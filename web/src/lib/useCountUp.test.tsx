import { describe, it, expect } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { useCountUp } from "./useCountUp";

function Probe({ to }: { to: number }) {
  const value = useCountUp(to, true, 0);
  return <span data-testid="v">{Math.round(value)}</span>;
}

describe("useCountUp", () => {
  it("settles on the target value when active", async () => {
    render(<Probe to={165} />);
    await waitFor(() => expect(screen.getByTestId("v").textContent).toBe("165"));
  });
});
