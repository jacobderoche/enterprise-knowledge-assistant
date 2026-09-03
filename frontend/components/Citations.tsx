import { Citation } from "@/lib/api";

export function Citations({ citations }: { citations: Citation[] }) {
  if (!citations || citations.length === 0) {
    return null;
  }
  return (
    <div className="citations">
      {citations.map((c, i) => (
        <div className="citation" key={c.chunk_id}>
          <span className="badge">[{i + 1}]</span>
          <strong>{c.source}</strong> · score {c.score.toFixed(2)}
          <div>{c.snippet}</div>
        </div>
      ))}
    </div>
  );
}
