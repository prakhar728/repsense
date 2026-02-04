"use client";

import { useState, useRef, useEffect, KeyboardEvent, ReactNode } from "react";
import Link from "next/link";
import { ChatMessage, getMockReply, suggestedPrompts } from "../lib/mockChat";
import { Spinner } from "./ui/Spinner";

function renderMessageContent(content: string): ReactNode {
  const parts = content.split(/(\[routine:[\w-]+\])/g);
  return parts.map((part, i) => {
    const match = part.match(/^\[routine:([\w-]+)\]$/);
    if (match) {
      return (
        <Link
          key={i}
          href={`/routine/${match[1]}`}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 my-1 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/25 text-sm font-medium transition-all"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M6.5 6.5v11M17.5 6.5v11M6.5 12h11M3.5 8.5v7M20.5 8.5v7" />
          </svg>
          View Routine
          <svg
            className="w-3.5 h-3.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
            />
          </svg>
        </Link>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

interface ChatScreenProps {
  messages: ChatMessage[];
  onSendMessage: (content: string) => void;
  isReplying: boolean;
  onToggleSidebar: () => void;
}

export function ChatScreen({
  messages,
  onSendMessage,
  isReplying,
  onToggleSidebar,
}: ChatScreenProps) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isReplying]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 160) + "px";
    }
  }, [input]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isReplying) return;
    onSendMessage(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="flex-1 flex flex-col h-full min-w-0">
      {/* Top bar */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-neutral-800 shrink-0">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-1.5 text-neutral-400 hover:text-white transition-colors rounded-lg hover:bg-neutral-800"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center">
            <svg
              className="w-4 h-4 text-white"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M6.5 6.5L17.5 17.5" />
              <path d="M17.5 6.5L6.5 17.5" />
              <circle cx="12" cy="12" r="9" />
            </svg>
          </div>
          <span className="text-sm font-semibold text-white">Repsense</span>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        {isEmpty ? (
          /* Empty state */
          <div className="flex flex-col items-center justify-center h-full px-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center mb-6 shadow-lg shadow-emerald-500/20">
              <svg
                className="w-8 h-8 text-white"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M6.5 6.5L17.5 17.5" />
                <path d="M17.5 6.5L6.5 17.5" />
                <circle cx="12" cy="12" r="9" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-white mb-2">
              How can I help you train?
            </h2>
            <p className="text-neutral-400 text-sm mb-8 text-center max-w-md">
              Ask me anything about your workout data, programming, recovery, or
              training optimization.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
              {suggestedPrompts.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => onSendMessage(prompt)}
                  className="text-left px-4 py-3 rounded-xl border border-neutral-800 hover:border-neutral-700 bg-neutral-900/50 hover:bg-neutral-800/50 text-sm text-neutral-300 hover:text-white transition-all"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Message list */
          <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
            {messages.map((msg) => (
              <div key={msg.id} className="flex gap-3">
                {msg.role === "assistant" ? (
                  <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center shrink-0 mt-0.5">
                    <svg
                      className="w-4 h-4 text-white"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M6.5 6.5L17.5 17.5" />
                      <path d="M17.5 6.5L6.5 17.5" />
                      <circle cx="12" cy="12" r="9" />
                    </svg>
                  </div>
                ) : (
                  <div className="w-7 h-7 rounded-lg bg-neutral-700 flex items-center justify-center shrink-0 mt-0.5">
                    <svg
                      className="w-4 h-4 text-neutral-300"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                      />
                    </svg>
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-neutral-500 mb-1">
                    {msg.role === "assistant" ? "Repsense" : "You"}
                  </p>
                  <div
                    className={`rounded-xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                      msg.role === "assistant"
                        ? "bg-neutral-800/50 text-neutral-200"
                        : "bg-emerald-500/10 text-neutral-200"
                    }`}
                  >
                    {renderMessageContent(msg.content)}
                  </div>
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {isReplying && (
              <div className="flex gap-3">
                <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center shrink-0 mt-0.5">
                  <svg
                    className="w-4 h-4 text-white"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M6.5 6.5L17.5 17.5" />
                    <path d="M17.5 6.5L6.5 17.5" />
                    <circle cx="12" cy="12" r="9" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="text-xs font-medium text-neutral-500 mb-1">
                    Repsense
                  </p>
                  <div className="bg-neutral-800/50 rounded-xl px-4 py-3 inline-flex items-center gap-1">
                    <Spinner size="sm" />
                    <span className="text-sm text-neutral-400 ml-2">
                      Thinking...
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="shrink-0 border-t border-neutral-800 p-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-end gap-2 bg-neutral-800/50 border border-neutral-700 rounded-xl px-4 py-2 focus-within:border-emerald-500 focus-within:ring-1 focus-within:ring-emerald-500 transition-all">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your training..."
              rows={1}
              className="flex-1 bg-transparent text-white placeholder-neutral-500 text-sm resize-none focus:outline-none py-1.5 max-h-40"
              disabled={isReplying}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isReplying}
              className="p-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 disabled:opacity-30 disabled:hover:bg-emerald-500 text-white transition-all shrink-0"
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
                  d="M5 12h14M12 5l7 7-7 7"
                />
              </svg>
            </button>
          </div>
          <p className="text-xs text-neutral-600 text-center mt-2">
            Repsense analyzes your workout data to provide personalized advice
          </p>
        </div>
      </div>
    </div>
  );
}
