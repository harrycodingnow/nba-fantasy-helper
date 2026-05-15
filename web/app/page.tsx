import { loadPlayers, loadSnapshot } from "@/lib/data";
import PlayerTable from "./PlayerTable";

export default function HomePage() {
  const players = loadPlayers();
  const snap = loadSnapshot();
  return (
    <>
      <div className="meta">
        Player Value Engine — points league. Data refreshed {new Date(snap.generated_at).toLocaleString()} ({snap.source_mode}). {snap.counts.players} players.
      </div>
      <PlayerTable players={players} />
    </>
  );
}
