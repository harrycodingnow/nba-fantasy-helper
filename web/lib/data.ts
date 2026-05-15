export type PlayerValue = {
  player_id: number;
  name: string;
  team: string;
  position: string;
  base_value: number;
  injury_risk_factor: number;
  opportunity_factor: number;
  minutes_factor: number;
  roster_factor: number;
  dynamic_value: number;
  risk_label: string;
  breakdown: {
    formula: string;
    inputs: Record<string, number | string>;
    multipliers: Record<string, number>;
  };
};

export type Opportunity = {
  player_id: number;
  name: string;
  team: string;
  position: string;
  projected_minutes: number;
  fpts_per_minute: number;
  games_this_week: number;
  opportunity_boost: number;
  weekly_value: number;
  why: string;
};

export type Snapshot = {
  generated_at: string;
  format: string;
  source_mode: "live" | "offline";
  schedule: {
    week_start: string;
    week_end: string | null;
    games_per_team: Record<string, number>;
  };
  counts: { players: number; opportunities: number };
};

import fs from "node:fs";
import path from "node:path";

function readJSON<T>(file: string): T {
  const p = path.join(process.cwd(), "public", "data", file);
  return JSON.parse(fs.readFileSync(p, "utf-8")) as T;
}

export function loadPlayers(): PlayerValue[] {
  return readJSON<PlayerValue[]>("players.json");
}
export function loadOpportunities(): Opportunity[] {
  return readJSON<Opportunity[]>("opportunities.json");
}
export function loadSnapshot(): Snapshot {
  return readJSON<Snapshot>("snapshot.json");
}
