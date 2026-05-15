import Link from "next/link";
import { loadPlayers, loadOpportunities } from "@/lib/data";

export function generateStaticParams() {
  return loadPlayers().map(p => ({ id: String(p.player_id) }));
}

export default function PlayerPage({ params }: { params: { id: string } }) {
  const id = Number(params.id);
  const players = loadPlayers();
  const ops = loadOpportunities();
  const p = players.find(x => x.player_id === id);
  if (!p) return <div>Unknown player {params.id}. <Link href="/">Back</Link></div>;
  const op = ops.find(x => x.player_id === id);

  const factors: Array<[string, number, string]> = [
    ["base_value", p.base_value, "fppg last season"],
    ["× injury_risk_factor", p.injury_risk_factor, `status=${p.breakdown.inputs.status}`],
    ["× opportunity_factor", p.opportunity_factor, `usage=${p.breakdown.inputs.usage_rate} pace_pct=${p.breakdown.inputs.team_pace_pct}`],
    ["× minutes_factor", p.minutes_factor, `last10_mpg=${p.breakdown.inputs.last10_mpg} season_mpg=${p.breakdown.inputs.season_mpg}`],
    ["× roster_factor", p.roster_factor, `depth_rank=${p.breakdown.inputs.depth_rank}`],
  ];

  return (
    <>
      <div className="meta"><Link href="/">← All players</Link></div>
      <h2 style={{ margin: "4px 0 4px" }}>{p.name} <span className="meta">({p.team} · {p.position || "—"})</span></h2>
      <div className="meta" style={{ marginBottom: 16 }}>{p.risk_label}</div>

      <div className="card">
        <div style={{ fontSize: 22, marginBottom: 4 }}>
          Dynamic value: <b>{p.dynamic_value.toFixed(2)}</b>
        </div>
        <div className="formula">{p.breakdown.formula}</div>
        <table style={{ marginTop: 12 }}>
          <thead><tr><th>Component</th><th className="num">Value</th><th>Driver</th><th>Visualization</th></tr></thead>
          <tbody>
            {factors.map(([name, val, driver]) => (
              <tr key={name}>
                <td>{name}</td>
                <td className="num">{val.toFixed(name === "base_value" ? 2 : 3)}</td>
                <td className="meta">{driver}</td>
                <td>
                  <span className="bar" style={{ width: `${Math.max(4, Math.min(160, val * (name === "base_value" ? 2 : 100)))}px` }} />
                </td>
              </tr>
            ))}
            <tr>
              <td><b>= dynamic_value</b></td>
              <td className="num"><b>{p.dynamic_value.toFixed(2)}</b></td>
              <td colSpan={2} />
            </tr>
          </tbody>
        </table>
      </div>

      {op && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>This week (Opportunity Engine)</h3>
          <dl className="kv">
            <dt>weekly_value</dt><dd><b>{op.weekly_value.toFixed(2)}</b></dd>
            <dt>projected_minutes</dt><dd>{op.projected_minutes}</dd>
            <dt>fpts_per_minute</dt><dd>{op.fpts_per_minute}</dd>
            <dt>games_this_week</dt><dd>{op.games_this_week}</dd>
            <dt>opportunity_boost</dt><dd>{op.opportunity_boost}</dd>
            <dt>why</dt><dd>{op.why}</dd>
          </dl>
          <div className="formula" style={{ marginTop: 8 }}>
            weekly_value = projected_minutes × fpts_per_minute × games_this_week × opportunity_boost
          </div>
        </div>
      )}

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Raw inputs</h3>
        <pre className="formula" style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(p.breakdown.inputs, null, 2)}</pre>
      </div>
    </>
  );
}
