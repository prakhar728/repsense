"use client";

import { useState } from "react";
import { Button } from "./ui/Button";
import { getMagic } from "../lib/magic";

interface LoginScreenProps {
  onLogin: () => void;
}

export function LoginScreen({ onLogin }: LoginScreenProps) {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsLoading(true);
    setError("");

    try {
      const magic = getMagic();
      await magic.auth.loginWithEmailOTP({ email });
      onLogin();
    } catch (err) {
      setError("Login failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      {/* Logo / Brand */}
      <div className="mb-12 text-center">
        <div className="mb-6 flex justify-center">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <svg
              className="w-10 h-10 text-white"
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
        </div>
        <h1 className="text-5xl font-black text-white tracking-tight mb-3">
          Repsense
        </h1>
        <p className="text-neutral-400 text-lg font-medium">
          Train smarter. Recover better.
        </p>
      </div>

      {/* Login Card */}
      <div className="w-full max-w-sm">
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-2xl p-8 backdrop-blur-sm">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-neutral-800/50 border border-neutral-700 text-white placeholder-neutral-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors"
                required
                disabled={isLoading}
              />
            </div>

            {error && (
              <p className="text-red-400 text-sm text-center">{error}</p>
            )}

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              disabled={isLoading || !email}
            >
              {isLoading ? "Sending code..." : "Continue with Email"}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-neutral-500 text-sm">
              We&apos;ll send you a one-time code to sign in.
            </p>
          </div>
        </div>

        {/* Features preview */}
        <div className="mt-10 grid grid-cols-3 gap-4 text-center">
          <div className="group">
            <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-neutral-800/50 border border-neutral-700/50 flex items-center justify-center group-hover:border-emerald-500/50 transition-colors">
              <svg
                className="w-6 h-6 text-neutral-400 group-hover:text-emerald-500 transition-colors"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <p className="text-xs text-neutral-500 font-medium">Analyze</p>
          </div>
          <div className="group">
            <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-neutral-800/50 border border-neutral-700/50 flex items-center justify-center group-hover:border-emerald-500/50 transition-colors">
              <svg
                className="w-6 h-6 text-neutral-400 group-hover:text-emerald-500 transition-colors"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <p className="text-xs text-neutral-500 font-medium">Optimize</p>
          </div>
          <div className="group">
            <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-neutral-800/50 border border-neutral-700/50 flex items-center justify-center group-hover:border-emerald-500/50 transition-colors">
              <svg
                className="w-6 h-6 text-neutral-400 group-hover:text-emerald-500 transition-colors"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <p className="text-xs text-neutral-500 font-medium">Progress</p>
          </div>
        </div>
      </div>
    </div>
  );
}
