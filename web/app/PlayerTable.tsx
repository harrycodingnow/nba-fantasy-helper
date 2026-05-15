"use client";
import { useMemo, useState } from "react";
import Link from "next/link";
import type { PlayerValue } from "@/lib/data";

function riskClass(label: string): string {
  if (label.toLowerCase().startsWith("high")) return "high";
  if (label.toLowerCase().startsWith("mid")) return "mid";
  return "low";
}

export default function PlayerTable({ players, basePath = "" }: { players: PlayerValue[]; basePath?: string }) {
  const [q, setQ] = useState("");
  const [team, setTeam] = useState("");
  const [pos, setPos] = useState("");
  const [sort, setSort] = useState<keyof PlayerValue>("dynamic_value");
  const [dir, setDir] = useState<1 | -1>(-1);

  const teams = useMemo(() => Array.from(new Set(players.map(p => p.team))).filter(Boolean).sort(), [players]);
  const positions = useMemo(() => Array.from(new Set(players.map(p => p.position))).filter(Boolean).sort(), [players]);

  const rows = useMemo(() => {
    const ql = q.toLowerCase();
    return players
      .filter(p => (ql ? p.name.toLowerCase().includes(ql) : true))
      .filter(p => (team ? p.team === team : true))
      .filter(p => (pos ? p.position === pos : true))
      .sort((a, b) => {
        const av = a[sort] as number | string;
        const bv = b[sort] as number | string;
        if (typeof av === "number" && typeof bv === "number") return (av - bv) * dir;
        return String(av).localeCompare(String(bv)) * dir;
      });
  }, [players, q, team, pos, sort, dir]);

  function header(key: keyof PlayerValue, label: string, numeric = false) {
    const arrow = sort === key ? (dir === -1 ? " ↓" : " ↑") : "";
    return (
      <th
        className={numeric ? "num" : ""}
        onClick={() => {
          if (sort === key) setDir(dir === -1 ? 1 : -1);
          else { setSort(key); setDir(-1); }
        }}
      >
        {label}{arrow}
      </th>
    );
  }

  return (
    <>
      <div className="filters">
        <input placeholder="Search player…" value={q} onChange={e => setQ(e.target.value)} />
        <select value={team} onChange={e => setTeam(e.target.value)}>
          <option value="">All teams</option>
          {teams.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <select value={pos} onChange={e => setPos(e.target.value)}>
          <option value="">All positions</option>
          {positions.map(p => <option key={p} value={p}>{p}</option>)}
        </select>
        <span className="meta" style={{ marginLeft: "auto" }}>{rows.length} players</span>
      </div>
      <table>
        <thead>
          <tr>
            {header("name", "Player")}
            {header("team", "Tm")}
            {header("position", "Pos")}
            {header("dynamic_value", "Dyn", true)}
            {header("base_value", "Base", true)}
            {header("injury_risk_factor", "×Inj", true)}
            {header("opportunity_factor", "×Opp", true)}
            {header("minutes_factor", "×Min", true)}
            {header("roster_factor", "×Rost", true)}
            <th>Risk label</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(p => (
            <tr key={p.player_id}>
              <td><Link href={`${basePath}/players/${p.player_id}/`}>{p.name}</Link></td>
              <td>{p.team}</td>
              <td>{p.position || "—"}</td>
              <td className="num"><b>{p.dynamic_value.toFixed(1)}</b></td>
              <td className="num">{p.base_value.toFixed(1)}</td>
              <td className="num">{p.injury_risk_factor.toFixed(2)}</td>
              <td className="num">{p.opportunity_factor.toFixed(2)}</td>
              <td className="num">{p.minutes_factor.toFixed(2)}</td>
              <td className="num">{p.roster_factor.toFixed(2)}</td>
              <td><span className={`badge ${riskClass(p.risk_label)}`}>{p.risk_label}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
