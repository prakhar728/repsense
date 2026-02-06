"use client";

import { useState } from "react";
import Image from "next/image";
import { Button } from "./ui/Button";
import { getMagic } from "../lib/magic";
import { Space_Grotesk } from "next/font/google";

const space = Space_Grotesk({ subsets: ["latin"], weight: ["400", "500", "600", "700"] });

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
    <div className={`min-h-screen ${space.className} text-white bg-neutral-950`}>
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(16,185,129,0.2),transparent_45%),radial-gradient(circle_at_70%_10%,rgba(56,189,248,0.2),transparent_40%)]" />
      <div className="relative z-10 flex min-h-screen items-center justify-center px-6">
        <div className="w-full max-w-md rounded-3xl border border-neutral-800 bg-neutral-900/60 p-8 backdrop-blur">
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 rounded-3xl bg-neutral-900/60 border border-emerald-500/30 flex items-center justify-center overflow-hidden shadow-[0_0_18px_rgba(16,185,129,0.2)]">
              <Image
                src="/assets/Logo.png?v=2"
                alt="Repsense"
                width={46}
                height={46}
                className="object-contain mix-blend-screen drop-shadow-[0_0_10px_rgba(16,185,129,0.35)]"
                priority
                unoptimized
              />
            </div>
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-neutral-500">
                Repsense
              </p>
              <h1 className="text-2xl font-semibold text-white">Sign in</h1>
            </div>
          </div>

          <p className="mt-4 text-sm text-neutral-400">
            Continue to your training cockpit and keep your data synced.
          </p>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <input
              type="email"
              placeholder="you@domain.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-2xl bg-neutral-950/60 border border-neutral-700 text-white placeholder-neutral-500 focus:outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400"
              required
              disabled={isLoading}
            />

            {error && (
              <p className="text-red-400 text-sm">{error}</p>
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

          <p className="mt-6 text-xs text-neutral-500">
            We&apos;ll send a one-time code. No passwords, just precision.
          </p>
        </div>
      </div>
    </div>
  );
}
