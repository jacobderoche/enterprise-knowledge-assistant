"use client";

import { useState } from "react";
import { DocumentResponse, uploadDocument } from "@/lib/api";

export function DocumentUpload({
  token,
  onUploaded,
}: {
  token: string;
  onUploaded: (doc: DocumentResponse) => void;
}) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [scope, setScope] = useState("public");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setError(null);
    setBusy(true);
    try {
      const doc = await uploadDocument(token, {
        title,
        source: title || "untitled",
        content,
        scope,
      });
      onUploaded(doc);
      setTitle("");
      setContent("");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  const disabled = busy || !token || !title.trim() || !content.trim();

  return (
    <div className="card">
      <h2>Upload document</h2>
      <label>Title</label>
      <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Employee Handbook" />
      <label>Access scope</label>
      <select value={scope} onChange={(e) => setScope(e.target.value)}>
        <option value="public">public</option>
        <option value="admin">admin</option>
        <option value="hr-confidential">hr-confidential</option>
      </select>
      <label>Content</label>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Paste document text to ingest into the knowledge base..."
      />
      <button onClick={submit} disabled={disabled}>
        {busy ? "Ingesting..." : "Upload & ingest"}
      </button>
      {error && <div className="error">{error}</div>}
    </div>
  );
}
