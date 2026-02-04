const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function uploadCSV(
  userId: string,
  file: File
): Promise<{ status: string }> {
  const formData = new FormData();
  formData.append("user_id", userId);
  formData.append("file", file);

  const res = await fetch(`${API_URL}/profile/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error(`Upload failed: ${res.statusText}`);
  }

  return res.json();
}

export async function sendMessage(
  userId: string,
  chatId: string,
  message: string
): Promise<{ type: string; text: string }> {
  const res = await fetch(`${API_URL}/chat/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, chat_id: chatId, message }),
  });

  if (!res.ok) {
    throw new Error(`Chat failed: ${res.statusText}`);
  }

  return res.json();
}

export interface SessionItem {
  id: string;
  created_at: string;
  last_message: string | null;
}

export async function getChatSessions(
  userId: string
): Promise<SessionItem[]> {
  const res = await fetch(`${API_URL}/chat/sessions/${encodeURIComponent(userId)}`);

  if (!res.ok) {
    throw new Error(`Failed to load sessions: ${res.statusText}`);
  }

  const data = await res.json();
  return data.sessions;
}

export interface MessageItem {
  role: string;
  content: string;
  routine_id: string | null;
  created_at: string;
}

export async function getChatMessages(
  userId: string,
  chatId: string
): Promise<MessageItem[]> {
  const res = await fetch(
    `${API_URL}/chat/sessions/${encodeURIComponent(userId)}/${encodeURIComponent(chatId)}/messages`
  );

  if (!res.ok) {
    throw new Error(`Failed to load messages: ${res.statusText}`);
  }

  const data = await res.json();
  return data.messages;
}

export async function getRoutine(
  routineId: string
): Promise<Record<string, unknown> | null> {
  const res = await fetch(`${API_URL}/routines/${encodeURIComponent(routineId)}`);

  if (!res.ok) {
    return null;
  }

  const data = await res.json();
  return data.routine;
}
