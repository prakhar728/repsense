"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getUserRoutines, RoutineSummary } from "../../lib/api";
import { Spinner } from "../../components/ui/Spinner";

export default function RoutinesHistoryPage() {
  const [routines, setRoutines] = useState<RoutineSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<"auth" | "generic" | null>(null);

  useEffect(() => {
    setLoading(true);
    getUserRoutines()
      .then((items) => setRoutines(items))
      .catch((err) => {
        if (err instanceof Error && err.message === "auth") {
          setError("auth");
        } else {
          setError("generic");
        }
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-950 text-white flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-neutral-950 text-white flex flex-col items-center justify-center px-4">
        <p className="text-neutral-400 mb-4">
          {error === "auth"
            ? "Please log in to view your routines."
            : "Unable to load routines."}
        </p>
        <Link
          href="/"
          className="text-emerald-500 hover:text-emerald-400 text-sm font-medium transition-colors"
        >
          Go back
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      <div className="sticky top-0 z-10 bg-neutral-950/90 backdrop-blur-md border-b border-neutral-800/50">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-white">Routine History</h1>
            <p className="text-sm text-neutral-400">All generated routines for your profile</p>
          </div>
          <Link
            href="/"
            className="text-sm text-neutral-400 hover:text-white transition-colors"
          >
            Back to chat
          </Link>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
        {routines.length === 0 ? (
          <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-900/40 text-neutral-400">
            No routines generated yet.
          </div>
        ) : (
          routines.map((routine) => (
            <Link
              key={routine.id}
              href={`/routine/${routine.id}`}
              className="block p-4 rounded-xl border border-neutral-800 bg-neutral-900/40 hover:bg-neutral-800/60 transition-all"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-white font-semibold">
                    {routine.title || "Generated Routine"}
                  </h3>
                  {routine.goal && (
                    <p className="text-sm text-neutral-400 mt-1">{routine.goal}</p>
                  )}
                  <div className="flex flex-wrap gap-2 mt-3">
                    {routine.days_per_week != null && (
                      <span className="text-xs text-emerald-300 bg-emerald-500/10 border border-emerald-500/20 px-2 py-1 rounded-full">
                        {routine.days_per_week} days/week
                      </span>
                    )}
                    {routine.focus_muscles?.map((muscle) => (
                      <span
                        key={muscle}
                        className="text-xs text-neutral-300 bg-neutral-800/70 border border-neutral-700 px-2 py-1 rounded-full"
                      >
                        {muscle}
                      </span>
                    ))}
                  </div>
                </div>
                <span className="text-xs text-neutral-500">
                  {new Date(routine.created_at).toLocaleString()}
                </span>
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
