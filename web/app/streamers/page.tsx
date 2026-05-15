import Link from "next/link";
import { loadOpportunities, loadSnapshot } from "@/lib/data";

export default function StreamersPage() {
  const ops = loadOpportunities();
  const snap = loadSnapshot();
  return (
    <>
      <div className="meta">
        Opportunity Engine — week {snap.schedule.week_start}{snap.schedule.week_end ? ` to ${snap.schedule.week_end}` : ""}. Top streamers ranked by projected weekly value (proj_min × fpts_per_min × games × boost).
      </div>
      <table>
        <thead>
          <tr>
            <th>Player</th><th>Tm</th><th className="num">Weekly</th><th className="num">Proj MPG</th>
            <th className="num">FPM</th><th className="num">Games</th><th className="num">Boost</th><th>Why</th>
          </tr>
        </thead>
        <tbody>
          {ops.slice(0, 50).map(o => (
            <tr key={o.player_id}>
              <td><Link href={`/players/${o.player_id}/`}>{o.name}</Link></td>
              <td>{o.team}</td>
              <td className="num"><b>{o.weekly_value.toFixed(1)}</b></td>
              <td className="num">{o.projected_minutes.toFixed(1)}</td>
              <td className="num">{o.fpts_per_minute.toFixed(2)}</td>
              <td className="num">{o.games_this_week}</td>
              <td className="num">{o.opportunity_boost.toFixed(2)}</td>
              <td>{o.why}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
