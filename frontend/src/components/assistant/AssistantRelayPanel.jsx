import { useEffect, useState } from 'react';
import apiFetch from '@/utils/apiClient';
import RelayComposer from './RelayComposer';
import RelayInbox from './RelayInbox';
import RelayOutbox from './RelayOutbox';

export default function AssistantRelayPanel({ slug }) {
  const [inbox, setInbox] = useState([]);
  const [outbox, setOutbox] = useState([]);
  const [assistants, setAssistants] = useState([]);
  const [recipient, setRecipient] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!slug) return;
    loadData();
  }, [slug]);

  async function loadData() {
    try {
      const [inData, outData, all] = await Promise.all([
        apiFetch(`/assistants/relay/inbox/${slug}`),
        apiFetch(`/assistants/relay/outbox/${slug}`),
        apiFetch('/assistants/')
      ]);
      setInbox(inData || []);
      setOutbox(outData || []);
      setAssistants(all || []);
    } catch (err) {
      console.error('Failed to load relay data', err);
    }
  }

  async function handleSend() {
    if (!recipient || !message) return;
    try {
      await apiFetch(`/assistants/${slug}/relay/`, {
        method: 'POST',
        body: { recipient_slug: recipient, message }
      });
      setMessage('');
      await loadData();
    } catch (err) {
      alert('Failed to send message');
    }
  }

  return (
    <div>
      <RelayComposer
        assistants={assistants.filter((a) => a.slug !== slug)}
        recipient={recipient}
        setRecipient={setRecipient}
        message={message}
        setMessage={setMessage}
        onSend={handleSend}
      />
      <h5>Outgoing</h5>
      <RelayOutbox messages={outbox} />
      <h5 className="mt-4">Incoming</h5>
      <RelayInbox messages={inbox} />
    </div>
  );
}
