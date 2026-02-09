"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Bebas_Neue, Space_Grotesk } from "next/font/google";
import { getMagic } from "../lib/magic";
import { getRoutine, getUserRoutines } from "../lib/api";

const bebas = Bebas_Neue({ subsets: ["latin"], weight: "400" });
const space = Space_Grotesk({ subsets: ["latin"], weight: ["400", "500", "600", "700"] });

export function LandingScreen() {
  const [metrics, setMetrics] = useState({
    fatigue: 0.68,
    load: 412,
    focus: "Posterior",
    isSample: true,
  });

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        const magic = getMagic();
        const loggedIn = await magic.user.isLoggedIn();
        if (!loggedIn) return;

        const routines = await getUserRoutines();
        if (!routines || routines.length === 0) return;

        const latest = routines[0];
        const routine = await getRoutine(latest.id);
        if (!routine) return;

        const sessions = Array.isArray(routine.sessions) ? routine.sessions : [];
        let totalSets = 0;
        const muscleCounts: Record<string, number> = {};

        sessions.forEach((session: any) => {
          const exercises = Array.isArray(session.exercises) ? session.exercises : [];
          exercises.forEach((ex: any) => {
            const sets = typeof ex.sets === "number" ? ex.sets : 0;
            totalSets += sets;
            const muscle = typeof ex.primary_muscle === "string" ? ex.primary_muscle : "";
            if (muscle) {
              muscleCounts[muscle] = (muscleCounts[muscle] || 0) + 1;
            }
          });
        });

        const topMuscle = Object.entries(muscleCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || "General";
        const fatigue = Math.min(1, Math.max(0.1, totalSets / 60));
        const load = totalSets || sessions.length * 8;

        setMetrics({
          fatigue: Number(fatigue.toFixed(2)),
          load,
          focus: topMuscle,
          isSample: false,
        });
      } catch {
        // Keep sample metrics
      }
    };

    loadMetrics();
  }, []);
  return (
    <div className={`min-h-screen ${space.className} text-white`}>
      <div className="relative min-h-screen overflow-hidden bg-neutral-950">
        {/* Atmospheric layers */}
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(16,185,129,0.18),transparent_45%),radial-gradient(circle_at_85%_30%,rgba(14,116,144,0.18),transparent_45%),radial-gradient(circle_at_50%_90%,rgba(168,85,247,0.12),transparent_55%)]" />
        <div
          className="pointer-events-none absolute inset-0 opacity-30"
          style={{
            backgroundImage:
              "linear-gradient(to right, rgba(255,255,255,0.06) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.04) 1px, transparent 1px)",
            backgroundSize: "80px 80px",
            maskImage: "radial-gradient(circle at 50% 30%, black 40%, transparent 75%)",
          }}
        />
        <div className="pointer-events-none absolute -top-24 left-1/2 h-[520px] w-[520px] -translate-x-1/2 rounded-full border border-emerald-500/30 blur-[0.5px]" />
        <div className="pointer-events-none absolute top-20 right-[-140px] h-[420px] w-[420px] rounded-full border border-cyan-400/20 blur-[0.5px]" />

        <div className="relative z-10 mx-auto flex min-h-screen max-w-6xl flex-col justify-between px-6 py-10 lg:flex-row lg:items-center lg:gap-12">
          {/* Left hero */}
          <div className="max-w-xl">
            <div className="flex items-center gap-4">
              <div className="h-16 w-16 rounded-3xl bg-neutral-900/60 border border-emerald-500/30 flex items-center justify-center shadow-[0_0_25px_rgba(16,185,129,0.25)] overflow-hidden">
                <Image
                  src="/assets/Logo.png?v=2"
                  alt="Repsense"
                  width={52}
                  height={52}
                  className="object-contain mix-blend-screen drop-shadow-[0_0_12px_rgba(16,185,129,0.35)]"
                  priority
                  unoptimized
                />
              </div>
              <span className="text-sm uppercase tracking-[0.3em] text-emerald-200/80">
                Repsense
              </span>
            </div>

            <h1 className={`mt-8 text-5xl sm:text-6xl lg:text-7xl font-bold leading-[0.9] ${bebas.className}`}>
              Train on a
              <span className="block bg-gradient-to-r from-emerald-300 via-cyan-300 to-emerald-300 bg-clip-text text-transparent">
                living dashboard
              </span>
            </h1>
            <p className="mt-6 text-lg text-neutral-300 leading-relaxed">
              Repsense turns every set into signal. Upload your history and get
              tailored routines generated from your training data.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              {[
                "Tailored routines",
                "Muscle-level insights",
                "Progress-aware suggestions",
                "Feedback loop AI",
              ].map((label) => (
                <span
                  key={label}
                  className="rounded-full border border-neutral-700/70 bg-neutral-900/40 px-4 py-1.5 text-sm text-neutral-200"
                >
                  {label}
                </span>
              ))}
            </div>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/"
                className="rounded-2xl bg-emerald-500 px-5 py-3 text-sm font-semibold text-neutral-950"
              >
                Enter the lab
              </Link>
              <a
                href="#pulse"
                className="rounded-2xl border border-neutral-700 px-5 py-3 text-sm font-semibold text-neutral-200"
              >
                See the signal
              </a>
            </div>

            {/* Faux data surface */}
            <div className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-3" id="pulse">
              {[
                { label: "Fatigue", value: metrics.fatigue.toFixed(2), valueClass: "text-emerald-300", barClass: "bg-emerald-400" },
                { label: "Load", value: metrics.load.toString(), valueClass: "text-cyan-300", barClass: "bg-cyan-400" },
                { label: "Focus", value: metrics.focus, valueClass: "text-violet-300", barClass: "bg-violet-400" },
              ].map((card) => (
                <div
                  key={card.label}
                  className="rounded-2xl border border-neutral-800 bg-neutral-900/40 p-4 backdrop-blur"
                >
                  <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">
                    {card.label}
                  </p>
                  <p className={`mt-2 text-2xl font-semibold ${card.valueClass}`}>
                    {card.value}
                  </p>
                  <div className="mt-3 h-1.5 w-full rounded-full bg-neutral-800">
                    <div
                      className={`h-1.5 rounded-full ${card.barClass}`}
                      style={{ width: metrics.isSample ? "72%" : `${Math.min(100, Math.max(20, metrics.fatigue * 100))}%` }}
                    />
                  </div>
                  {metrics.isSample && (
                    <p className="mt-2 text-[10px] uppercase tracking-[0.2em] text-neutral-600">
                      Sample
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Right panel */}
          <div className="mt-12 w-full max-w-md lg:mt-0">
            <div className="rounded-3xl border border-neutral-800 bg-neutral-900/50 p-8 backdrop-blur-xl shadow-[0_0_60px_rgba(16,185,129,0.15)]">
              <p className="text-sm uppercase tracking-[0.3em] text-neutral-500">
                Signal stack
              </p>
              <h2 className="mt-2 text-3xl font-semibold text-white">
                Your workouts, decoded
              </h2>
              <p className="mt-3 text-sm text-neutral-400">
                Every session feeds the model. Repsense extracts muscle intent,
                fatigue, and recovery windows to keep you growing.
              </p>

              <div className="mt-6 space-y-4 text-sm text-neutral-300">
                <div className="flex items-start gap-3">
                  <span className="h-2 w-2 mt-2 rounded-full bg-emerald-400" />
                  <p>Routine generator tuned to your volume and capacity.</p>
                </div>
                <div className="flex items-start gap-3">
                  <span className="h-2 w-2 mt-2 rounded-full bg-cyan-400" />
                  <p>Instant feedback capture with historical context.</p>
                </div>
                <div className="flex items-start gap-3">
                  <span className="h-2 w-2 mt-2 rounded-full bg-violet-400" />
                  <p>Granular muscle targeting and weekly focus balance.</p>
                </div>
              </div>
            </div>

            <div className="mt-6 flex items-center justify-between text-xs text-neutral-500">
              <span>Built for lifters who measure everything.</span>
              <span>v0.1 beta</span>
            </div>
          </div>
        </div>

        {/* Feature grid */}
        <section className="relative z-10 mx-auto max-w-6xl px-6 pb-24">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[
              {
                title: "Muscle intelligence",
                body: "Muscle mapping translates your logs into clear training targets.",
              },
              {
                title: "Progress-aware guidance",
                body: "Use your training history to shape future routine recommendations.",
              },
              {
                title: "Routine memory",
                body: "Every routine is stored, versioned, and ready to iterate.",
              },
              {
                title: "Feedback fusion",
                body: "Injury notes and wins are fed back into the next plan.",
              },
              {
                title: "Session clarity",
                body: "Daily sessions are broken into focus blocks with clean cues.",
              },
              {
                title: "History view",
                body: "Scan past routines and learn what actually worked.",
              },
            ].map((feature) => (
              <div
                key={feature.title}
                className="rounded-3xl border border-neutral-800 bg-neutral-900/40 p-6 backdrop-blur"
              >
                <h3 className="text-lg font-semibold text-white">
                  {feature.title}
                </h3>
                <p className="mt-3 text-sm text-neutral-400">{feature.body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Process section */}
        <section className="relative z-10 mx-auto max-w-6xl px-6 pb-24">
          <div className="grid gap-8 lg:grid-cols-[1.2fr_1fr] lg:items-center">
            <div>
              <h2 className={`text-4xl sm:text-5xl font-bold ${bebas.className}`}>
                Your data becomes a training engine
              </h2>
              <p className="mt-4 text-neutral-300">
                Upload once, then let the system learn your history. Repsense
                uses your logs and feedback to guide the next routine and keep
                the week aligned with your goal.
              </p>
              <div className="mt-6 space-y-4">
                {[
                  { step: "01", label: "Upload your training history" },
                  { step: "02", label: "Get a tailored program instantly" },
                  { step: "03", label: "Log feedback to evolve it weekly" },
                ].map((item) => (
                  <div
                    key={item.step}
                    className="flex items-center gap-4 rounded-2xl border border-neutral-800 bg-neutral-900/40 px-4 py-3"
                  >
                    <span className="text-sm font-semibold text-emerald-300">
                      {item.step}
                    </span>
                    <span className="text-sm text-neutral-200">{item.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-3xl border border-neutral-800 bg-neutral-900/50 p-6">
              <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-neutral-500">
                <span>Week snapshot</span>
                <span>Load 412</span>
              </div>
              <div className="mt-6 space-y-4">
                {[
                  { day: "Mon", focus: "Posterior chain", color: "bg-emerald-400" },
                  { day: "Wed", focus: "Upper power", color: "bg-cyan-400" },
                  { day: "Fri", focus: "Leg density", color: "bg-violet-400" },
                ].map((session) => (
                  <div
                    key={session.day}
                    className="rounded-2xl border border-neutral-800 bg-neutral-950/60 p-4"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-neutral-200">{session.day}</span>
                      <span className="text-xs text-neutral-500">{session.focus}</span>
                    </div>
                    <div className="mt-3 h-2 w-full rounded-full bg-neutral-800">
                      <div className={`h-2 rounded-full ${session.color}`} style={{ width: "78%" }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Testimonials */}
        <section className="relative z-10 mx-auto max-w-6xl px-6 pb-24">
          <div className="grid gap-6 md:grid-cols-3">
            {[
              {
                quote:
                  "The routines stopped guessing. It feels like a coach that remembers.",
                name: "K. Ortiz",
                role: "Powerlifting",
              },
              {
                quote:
                  "I finally know how much volume I can push without crashing.",
                name: "M. Singh",
                role: "Hypertrophy",
              },
              {
                quote:
                  "The history view makes weekly adjustments obvious and fast.",
                name: "A. Park",
                role: "Cross-training",
              },
            ].map((item) => (
              <div
                key={item.name}
                className="rounded-3xl border border-neutral-800 bg-neutral-900/40 p-6"
              >
                <p className="text-sm text-neutral-300">“{item.quote}”</p>
                <div className="mt-4 text-xs uppercase tracking-[0.2em] text-neutral-500">
                  {item.name} · {item.role}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Final CTA */}
        <section className="relative z-10 mx-auto max-w-6xl px-6 pb-24">
          <div className="rounded-3xl border border-neutral-800 bg-gradient-to-r from-emerald-500/10 via-neutral-900/60 to-cyan-500/10 p-8 text-center">
            <h2 className={`text-4xl sm:text-5xl font-bold ${bebas.className}`}>
              Ready to feel the signal?
            </h2>
            <p className="mt-4 text-neutral-300">
              Jump into Repsense and let your next routine adapt instantly.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <Link
                href="/"
                className="rounded-2xl bg-emerald-500 px-6 py-3 text-sm font-semibold text-neutral-950"
              >
                Sign in now
              </Link>
              <Link
                href="/"
                className="rounded-2xl border border-neutral-700 px-6 py-3 text-sm font-semibold text-neutral-200"
              >
                Upload history
              </Link>
            </div>
          </div>
        </section>

        {/* Floating graphic */}
        <div className="pointer-events-none absolute bottom-10 left-1/2 hidden -translate-x-1/2 lg:block">
          <svg width="420" height="110" viewBox="0 0 420 110" fill="none">
            <path
              d="M10 90C60 20 140 20 190 70C240 120 320 120 410 40"
              stroke="url(#pulseGradient)"
              strokeWidth="3"
              strokeLinecap="round"
              strokeDasharray="6 10"
            />
            <defs>
              <linearGradient id="pulseGradient" x1="10" y1="90" x2="410" y2="40" gradientUnits="userSpaceOnUse">
                <stop stopColor="#34D399" />
                <stop offset="0.5" stopColor="#22D3EE" />
                <stop offset="1" stopColor="#A855F7" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>
    </div>
  );
}
