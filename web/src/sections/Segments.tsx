import { Section } from "../components/Section";
import { SegmentDonut } from "../components/charts/SegmentDonut";
import { SessionDepthChart } from "../components/charts/SessionDepthChart";
import { CategoryBars } from "../components/charts/CategoryBars";
import { Takeaway } from "../components/Takeaway";
import { metrics } from "../lib/data";

export function Segments({ onActive }: { onActive: (id: string) => void }) {
  return (
    <Section id="segments" title="用户分层与品类" onActive={onActive}>
      {(active) => (
        <>
          <div className="grid md:grid-cols-2 gap-8">
            <SegmentDonut data={metrics.segments} active={active} />
            <SessionDepthChart data={metrics.session_depth} active={active} />
          </div>
          <div className="mt-10"><CategoryBars data={metrics.category} active={active} /></div>
          <Takeaway>最大群体是 Browsers Only；购买/复购用户是精细化运营与资源倾斜的重点。</Takeaway>
        </>
      )}
    </Section>
  );
}
