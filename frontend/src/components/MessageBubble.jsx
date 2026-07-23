export default function MessageBubble({ role, text, children }) {
  return (
    <div className={`bubble ${role}`}>
      <p className="bubble-text">{text}</p>
      {children}
    </div>
  )
}
