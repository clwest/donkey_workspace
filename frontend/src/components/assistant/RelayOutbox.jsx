export default function RelayOutbox({ messages = [] }) {
  if (!messages.length) {
    return <div>No outgoing messages.</div>;
  }
  return (
    <table className="table table-sm">
      <thead>
        <tr>
          <th>Recipient</th>
          <th>Preview</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {messages.map((m) => (
          <tr key={m.id}>
            <td>{m.recipient}</td>
            <td>{m.content.slice(0, 30)}...</td>
            <td>{m.responded ? '✨ Responded' : m.delivered ? '✅ Delivered' : '🕓 Pending'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
