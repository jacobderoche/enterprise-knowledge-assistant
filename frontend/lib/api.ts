export interface Citation {
  chunk_id: string;
  document_id: string;
  source: string;
  score: number;
  snippet: string;
}

export interface ChatResponse {
  conversationId: string;
  messageId: string;
  answer: string;
  citations: Citation[];
  model: string;
  usedContext: boolean;
}

export interface DocumentResponse {
  id: string;
  title: string;
  source: string;
  scope: string;
  chunkCount: number;
  createdAt: string;
}

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8080";

function authHeaders(token: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed (${res.status}): ${text}`);
  }
  return res.json() as Promise<T>;
}

export async function uploadDocument(
  token: string,
  input: { title: string; source: string; content: string; scope: string }
): Promise<DocumentResponse> {
  const res = await fetch(`${BACKEND_URL}/api/documents`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(input),
  });
  return handle<DocumentResponse>(res);
}

export async function listDocuments(token: string): Promise<DocumentResponse[]> {
  const res = await fetch(`${BACKEND_URL}/api/documents`, {
    headers: authHeaders(token),
  });
  return handle<DocumentResponse[]>(res);
}

export async function sendChat(
  token: string,
  input: { message: string; conversationId?: string }
): Promise<ChatResponse> {
  const res = await fetch(`${BACKEND_URL}/api/chat`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(input),
  });
  return handle<ChatResponse>(res);
}

export async function sendFeedback(
  token: string,
  input: { messageId: string; rating: number; comment?: string }
): Promise<void> {
  const res = await fetch(`${BACKEND_URL}/api/feedback`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(input),
  });
  await handle(res);
}
