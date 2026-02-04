"use client";

import { useState, useCallback } from "react";
import { Sidebar } from "./Sidebar";
import { ChatScreen } from "./ChatScreen";
import {
  ChatMessage,
  mockSessions,
  getMockReply,
} from "../lib/mockChat";

interface ChatLayoutProps {
  userEmail: string;
  onLogout: () => void;
}

export function ChatLayout({ userEmail, onLogout }: ChatLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isReplying, setIsReplying] = useState(false);

  const handleNewChat = useCallback(() => {
    setActiveSessionId(null);
    setMessages([]);
    setSidebarOpen(false);
  }, []);

  const handleSelectSession = useCallback((id: string) => {
    setActiveSessionId(id);
    // In a real app, load messages for this session
    setMessages([]);
    setSidebarOpen(false);
  }, []);

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
        const reply = await getMockReply();
        const assistantMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: reply,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } finally {
        setIsReplying(false);
      }
    },
    []
  );

  return (
    <div className="flex h-screen bg-neutral-950 text-white">
      <Sidebar
        sessions={mockSessions}
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
