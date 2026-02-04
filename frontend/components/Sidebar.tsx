"use client";

import { ChatSession } from "../lib/mockChat";

interface SidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onLogout: () => void;
  userEmail: string;
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onLogout,
  userEmail,
  isOpen,
  onClose,
}: SidebarProps) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 h-full w-64 bg-neutral-900 border-r border-neutral-800 z-40
          flex flex-col transition-transform duration-200
          lg:relative lg:translate-x-0
          ${isOpen ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        {/* Header */}
        <div className="p-4 border-b border-neutral-800">
          <button
            onClick={onNewChat}
            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl border border-neutral-700 hover:border-neutral-600 text-neutral-300 hover:text-white text-sm font-medium transition-all active:scale-[0.98]"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            New chat
          </button>
        </div>

        {/* Chat history */}
        <div className="flex-1 overflow-y-auto p-2">
          {sessions.map((session) => {
            const isActive = session.id === activeSessionId;
            return (
              <button
                key={session.id}
                onClick={() => onSelectSession(session.id)}
                className={`
                  w-full text-left px-3 py-2.5 rounded-xl mb-1 transition-all text-sm
                  ${
                    isActive
                      ? "bg-emerald-500/10 text-white"
                      : "text-neutral-400 hover:bg-neutral-800 hover:text-neutral-200"
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <svg
                    className={`w-4 h-4 shrink-0 ${isActive ? "text-emerald-500" : "text-neutral-600"}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                  <span className="truncate">{session.title}</span>
                </div>
                <p className="text-xs text-neutral-600 mt-1 ml-6">
                  {session.date}
                </p>
              </button>
            );
          })}
        </div>

        {/* User section */}
        <div className="p-3 border-t border-neutral-800">
          <div className="flex items-center gap-3 px-2 py-2">
            <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0">
              <span className="text-emerald-400 text-sm font-semibold">
                {userEmail.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-neutral-300 truncate">{userEmail}</p>
            </div>
            <button
              onClick={onLogout}
              className="p-1.5 text-neutral-500 hover:text-neutral-300 transition-colors rounded-lg hover:bg-neutral-800"
              title="Log out"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
