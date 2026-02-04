"use client";

import { useState, useCallback, useEffect } from "react";
import { Sidebar } from "./Sidebar";
import { ChatScreen } from "./ChatScreen";
import { ChatMessage, ChatSession } from "../lib/mockChat";
import {
  sendMessage,
  getChatSessions,
  getChatMessages,
  SessionItem,
} from "../lib/api";

interface ChatLayoutProps {
  userEmail: string;
  onLogout: () => void;
}

function generateId(): string {
  return crypto.randomUUID();
}

function toSidebarSessions(items: SessionItem[]): ChatSession[] {
  return items.map((s) => ({
    id: s.id,
    title: s.last_message
      ? s.last_message.slice(0, 40) + (s.last_message.length > 40 ? "..." : "")
      : "New chat",
    lastMessage: s.last_message || "",
    date: new Date(s.created_at).toLocaleDateString(),
  }));
}

export function ChatLayout({ userEmail, onLogout }: ChatLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [chatId, setChatId] = useState<string>(generateId());
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isReplying, setIsReplying] = useState(false);
  const [sessions, setSessions] = useState<ChatSession[]>([]);

  // Load sessions on mount
  useEffect(() => {
    getChatSessions(userEmail)
      .then((items) => setSessions(toSidebarSessions(items)))
      .catch(() => {});
  }, [userEmail]);

  const handleNewChat = useCallback(() => {
    setActiveSessionId(null);
    setChatId(generateId());
    setMessages([]);
    setSidebarOpen(false);
  }, []);

  const handleSelectSession = useCallback(
    async (id: string) => {
      setActiveSessionId(id);
      setChatId(id);
      setSidebarOpen(false);

      try {
        const apiMessages = await getChatMessages(userEmail, id);
        setMessages(
          apiMessages.map((m, i) => ({
            id: `${id}-${i}`,
            role: m.role as "user" | "assistant",
            content: m.content,
            timestamp: new Date(m.created_at),
          }))
        );
      } catch {
        setMessages([]);
      }
    },
    [userEmail]
  );

  const handleSendMessage = useCallback(
    async (content: string) => {
      const userMsg: ChatMessage = {
        id: Date.now().toString(),
        role: "user",
        content,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMsg]);
      setIsReplying(true);

      try {
        const res = await sendMessage(userEmail, chatId, content);
        const assistantMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: res.text,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMsg]);

        // Refresh sessions list
        getChatSessions(userEmail)
          .then((items) => setSessions(toSidebarSessions(items)))
          .catch(() => {});

        if (!activeSessionId) {
          setActiveSessionId(chatId);
        }
      } catch {
        const errorMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "Something went wrong. Please try again.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMsg]);
      } finally {
        setIsReplying(false);
      }
    },
    [userEmail, chatId, activeSessionId]
  );

  return (
    <div className="flex h-screen bg-neutral-950 text-white">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onLogout={onLogout}
        userEmail={userEmail}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      <ChatScreen
        messages={messages}
        onSendMessage={handleSendMessage}
        isReplying={isReplying}
        onToggleSidebar={() => setSidebarOpen((o) => !o)}
      />
    </div>
  );
}
