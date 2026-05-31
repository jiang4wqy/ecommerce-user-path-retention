import { useState } from "react";
import { ProgressRail } from "./components/ProgressRail";
import { Hero } from "./sections/Hero";
import { Overview } from "./sections/Overview";
import { Conversion } from "./sections/Conversion";
import { Retention } from "./sections/Retention";
import { UserPath } from "./sections/UserPath";
import { Segments } from "./sections/Segments";
import { Insights } from "./sections/Insights";

const RAIL = [
  { id: "overview", label: "整体" },
  { id: "conversion", label: "转化" },
  { id: "retention", label: "留存" },
  { id: "userpath", label: "路径" },
  { id: "segments", label: "分层" },
  { id: "insights", label: "洞察" },
];

export default function App() {
  const [active, setActive] = useState("overview");
  return (
    <>
      <ProgressRail sections={RAIL} active={active} />
      <Hero />
      <Overview onActive={setActive} />
      <Conversion onActive={setActive} />
      <Retention onActive={setActive} />
      <UserPath onActive={setActive} />
      <Segments onActive={setActive} />
      <Insights onActive={setActive} />
    </>
  );
}
