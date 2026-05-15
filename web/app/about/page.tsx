import { loadSnapshot } from "@/lib/data";

export default function AboutPage() {
  const snap = loadSnapshot();
  return (
    <div className="card">
      <h2 style={{ marginTop: 0 }}>About</h2>
      <p>NBA Fantasy Helper, points-league only (v1). Two engines:</p>
      <ul>
        <li><b>Player Value</b>: <code>dynamic_value = base × injury × opportunity × minutes × roster</code></li>
        <li><b>Opportunity</b>: <code>weekly_value = proj_min × fpm × games × boost</code></li>
      </ul>
      <p>Click any player to see the multiplier breakdown.</p>
      <p className="meta">
        Snapshot generated {new Date(snap.generated_at).toLocaleString()} from <b>{snap.source_mode}</b> data.
        See README.md for refresh instructions and known limitations.
      </p>
    </div>
  );
}
