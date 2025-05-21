import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function LoreTokenExchangeForm({ senderId }) {
  const [tokenId, setTokenId] = useState("");
  const [receiverId, setReceiverId] = useState("");
  const [intent, setIntent] = useState("gift");
  const [context, setContext] = useState("");

  async function submit() {
    try {
      await apiFetch("/lore-tokens/exchange/", {
        method: "POST",
        body: {
          token: tokenId,
          sender: senderId,
          receiver: receiverId,
          intent,
          context,
        },
      });
      setTokenId("");
      setReceiverId("");
      setContext("");
    } catch (err) {
      console.error("Failed to exchange token", err);
    }
  }

  return (
    <div className="my-3">
      <h5>Send Lore Token</h5>
      <input
        className="form-control mb-1"
        placeholder="Token ID"
        value={tokenId}
        onChange={(e) => setTokenId(e.target.value)}
      />
      <input
        className="form-control mb-1"
        placeholder="Receiver Assistant ID"
        value={receiverId}
        onChange={(e) => setReceiverId(e.target.value)}
      />
      <input
        className="form-control mb-1"
        placeholder="Intent"
        value={intent}
        onChange={(e) => setIntent(e.target.value)}
      />
      <textarea
        className="form-control mb-2"
        rows="2"
        placeholder="Context"
        value={context}
        onChange={(e) => setContext(e.target.value)}
      />
      <button className="btn btn-primary" onClick={submit}>
        Send
      </button>
    </div>
  );
}
