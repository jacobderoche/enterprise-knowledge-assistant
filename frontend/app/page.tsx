"use client";

import { useEffect, useState } from "react";
import { DocumentResponse, listDocuments } from "@/lib/api";
import { DocumentUpload } from "@/components/DocumentUpload";
import { ChatPanel } from "@/components/ChatPanel";

export default function Home() {
  const [token, setToken] = useState("");
  const [docs, setDocs] = useState<DocumentResponse[]>([]);

  useEffect(() => {
    const saved = typeof window !== "undefined" ? localStorage.getItem("ka_token") : null;
    if (saved) setToken(saved);
  }, []);

  useEffect(() => {
    if (!token) return;
    localStorage.setItem("ka_token", token);
    listDocuments(token)
      .then(setDocs)
      .catch(() => setDocs([]));
  }, [token]);

  return (
    <div className="container">
      <div className="header">
        <h1>🔐 Enterprise Knowledge Assistant</h1>
        <div style={{ width: 380 }}>
          <input
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="Paste JWT access token"
          />
        </div>
      </div>

      {!token && (
        <div className="card">
          <p className="muted">
            Paste a JWT to begin. In local dev, mint an HS256 token signed with the
            backend&apos;s <code>app.jwt-secret</code> containing <code>sub</code> and a{" "}
            <code>roles</code> claim (e.g. <code>[&quot;employee&quot;]</code>). See the
            root README for a one-liner.
          </p>
        </div>
      )}

      <div className="grid">
        <div>
          <DocumentUpload
            token={token}
            onUploaded={(doc) => setDocs((d) => [doc, ...d])}
          />
          <div className="card" style={{ marginTop: 20 }}>
            <h2>Visible documents</h2>
            {docs.length === 0 && <div className="muted">No documents yet.</div>}
            {docs.map((d) => (
              <div className="doc-item" key={d.id}>
                <strong>{d.title}</strong>
                <div className="muted">
                  {d.scope} · {d.chunkCount} chunks
                </div>
              </div>
            ))}
          </div>
        </div>
        <ChatPanel token={token} />
      </div>
    </div>
  );
}
