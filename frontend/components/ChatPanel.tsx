"use client";

import { useState } from "react";
import { Citation, ChatResponse, sendChat, sendFeedback } from "@/lib/api";
import { Citations } from "./Citations";

interface DisplayMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  usedContext?: boolean;
}

export function ChatPanel({ token }: { token: string }) {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send() {
    if (!input.trim()) return;
    const question = input;
    setInput("");
    setError(null);
    setMessages((m) => [...m, { id: `u-${Date.now()}`, role: "user", content: question }]);
    setBusy(true);
    try {
      const res: ChatResponse = await sendChat(token, { message: question, conversationId });
      setConversationId(res.conversationId);
      setMessages((m) => [
        ...m,
        {
          id: res.messageId,
          role: "assistant",
          content: res.answer,
          citations: res.citations,
          usedContext: res.usedContext,
        },
      ]);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function rate(messageId: string, rating: number) {
    try {
      await sendFeedback(token, { messageId, rating });
    } catch {
      /* non-blocking */
    }
  }

  return (
    <div className="card">
      <h2>Ask the knowledge base</h2>
      <div className="messages">
        {messages.length === 0 && (
          <div className="muted">Upload a document, then ask a question to get a cited answer.</div>
        )}
        {messages.map((m) => (
          <div key={m.id} className={`msg ${m.role}`}>
            <div>{m.content}</div>
            {m.role === "assistant" && (
              <>
                {m.usedContext === false && (
                  <div className="muted">No permitted source matched this question.</div>
                )}
                <Citations citations={m.citations ?? []} />
                <div className="row">
                  <button onClick={() => rate(m.id, 1)}>👍</button>
                  <button onClick={() => rate(m.id, -1)}>👎</button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="e.g. How many PTO days do employees get?"
      />
      <button onClick={send} disabled={busy || !token || !input.trim()}>
        {busy ? "Thinking..." : "Send"}
      </button>
      {error && <div className="error">{error}</div>}
    </div>
  );
}
