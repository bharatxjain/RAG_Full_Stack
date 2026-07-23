export default function SourceList({ sources }) {
  if (!sources || sources.length === 0) return null

  return (
    <div className="source-list">
      {sources.map((s, i) => (
        <span key={i} className="source-tag">
          {s.source} · {s.score}
        </span>
      ))}
    </div>
  )
}
