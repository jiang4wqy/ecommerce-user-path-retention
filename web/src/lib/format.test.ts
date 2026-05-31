import { describe, it, expect } from "vitest";
import { fmtInt, fmtPct, fmtMoney } from "./format";

describe("format", () => {
  it("formats integers with thousands separators", () => {
    expect(fmtInt(41944)).toBe("41,944");
  });
  it("formats percentages from a 0-1 ratio", () => {
    expect(fmtPct(0.181)).toBe("18.1%");
  });
  it("formats money compactly", () => {
    expect(fmtMoney(89124.16)).toBe("¥89,124");
  });
});
