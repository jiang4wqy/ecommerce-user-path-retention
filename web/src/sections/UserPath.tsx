import { Section } from "../components/Section";
import { PathBars } from "../components/charts/PathBars";
import { PurchasePathCompare } from "../components/charts/PurchasePathCompare";
import { Takeaway } from "../components/Takeaway";
import { metrics } from "../lib/data";

export function UserPath({ onActive }: { onActive: (id: string) => void }) {
  return (
    <Section id="userpath" title="用户路径" onActive={onActive}>
      {(active) => (
        <>
          <PathBars data={metrics.paths} active={active} />
          <div className="mt-10"><PurchasePathCompare data={metrics.purchase_paths} /></div>
          <Takeaway>多数 session 停在浏览阶段；购买 session 的行为序列更长、更聚焦。</Takeaway>
        </>
      )}
    </Section>
  );
}
