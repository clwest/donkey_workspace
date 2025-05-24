export default function RelayComposer({ assistants = [], recipient, setRecipient, message, setMessage, onSend }) {
  return (
    <div className="mb-3">
      <select className="form-select mb-2" value={recipient} onChange={(e) => setRecipient(e.target.value)}>
        <option value="">Select Assistant...</option>
        {assistants.map((a) => (
          <option key={a.id} value={a.slug}>
            {a.name}
          </option>
        ))}
      </select>
      <textarea
        className="form-control mb-2"
        rows="3"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type a message..."
      ></textarea>
      <button className="btn btn-primary" onClick={onSend} disabled={!recipient || !message}>
        Send
      </button>
    </div>
  );
}
