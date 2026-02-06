const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getAuthHeaders(): Promise<HeadersInit> {
  try {
    const { getMagic } = await import("./magic");
    const magic = getMagic();
    const isLoggedIn = await magic.user.isLoggedIn();
    if (!isLoggedIn) {
      console.warn("Auth: Magic reports user is not logged in.");
      return {};
    }
    let token = await magic.user.getIdToken({ forceRefresh: true });
    if (!token) {
      await new Promise((resolve) => setTimeout(resolve, 250));
      token = await magic.user.getIdToken({ forceRefresh: true });
    }
    if (!token) {
      console.warn("Auth: Magic did not return an ID token.");
      return {};
    }
    return { Authorization: `Bearer ${token}` };
  } catch {
    console.warn("Auth: failed to obtain Magic token.");
    return {};
  }
}

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

export async function getUserProfileStatus(
  userId: string
): Promise<{ exists: boolean; user_id?: string; message?: string }> {
  const res = await fetch(
    `${API_URL}/profile/${encodeURIComponent(userId)}`
  );

  if (!res.ok) {
    throw new Error(`Failed to load profile: ${res.statusText}`);
  }

  return res.json();
}

export async function getRoutine(
  routineId: string
): Promise<Record<string, unknown> | null> {
  const authHeaders = await getAuthHeaders();
  const res = await fetch(
    `${API_URL}/routines/${encodeURIComponent(routineId)}`,
    { headers: authHeaders }
  );

  if (res.status === 401 || res.status === 403) {
    throw new Error("auth");
  }

  if (!res.ok) {
    return null;
  }

  const data = await res.json();
  return data.routine;
}

export interface RoutineSummary {
  id: string;
  created_at: string;
  title: string;
  goal: string;
  days_per_week?: number | null;
  focus_muscles?: string[];
}

export async function getUserRoutines(
): Promise<RoutineSummary[]> {
  const authHeaders = await getAuthHeaders();
  const res = await fetch(
    `${API_URL}/routines`,
    { headers: authHeaders }
  );

  if (res.status === 401 || res.status === 403) {
    throw new Error("auth");
  }

  if (!res.ok) {
    throw new Error(`Failed to load routines: ${res.statusText}`);
  }

  const data = await res.json();
  return data.routines;
}

export interface GeneratedRoutine {
  routine_id: string;
  routine: {
    title: string;
    goal: string;
    level: string;
    plan_type: string;
    duration: { weeks: number | null; days_per_week: number | null };
    sessions: {
      day: string;
      focus: string;
      exercises: {
        name: string;
        primary_muscle: string;
        sets: number;
        reps: string;
        suggested_weight_kg: number | null;
        rest_seconds: number;
        notes: string;
      }[];
    }[];
  };
}

export async function generateRoutinesFromGoal(
  userId: string,
  goal: string
): Promise<GeneratedRoutine> {
  const res = await fetch(`${API_URL}/profile/generate-routines`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, goal }),
  });

  if (!res.ok) {
    throw new Error(`Routine generation failed: ${res.statusText}`);
  }

  return res.json();
}
