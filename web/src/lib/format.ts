export const fmtInt = (n: number): string => Math.round(n).toLocaleString("en-US");

export const fmtPct = (ratio: number, digits = 1): string =>
  `${(ratio * 100).toFixed(digits)}%`;

export const fmtMoney = (n: number): string => `¥${Math.round(n).toLocaleString("en-US")}`;
