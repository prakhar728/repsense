"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getRoutine } from "../../../lib/api";
import { Spinner } from "../../../components/ui/Spinner";

export default function RoutinePage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [routine, setRoutine] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<"auth" | "generic" | null>(null);

  useEffect(() => {
    setLoading(true);
    getRoutine(id)
      .then((data) => {
        setRoutine(data);
        if (!data) setError("generic");
      })
      .catch((err) => {
        if (err instanceof Error && err.message === "auth") {
          setError("auth");
        } else {
          setError("generic");
        }
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-950 text-white flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !routine) {
    return (
      <div className="min-h-screen bg-neutral-950 text-white flex flex-col items-center justify-center px-4">
        <p className="text-neutral-400 mb-4">
          {error === "auth"
            ? "Please log in to view this routine."
            : "Routine not found"}
        </p>
        <button
          onClick={() => router.back()}
          className="text-emerald-500 hover:text-emerald-400 text-sm font-medium transition-colors"
        >
          Go back
        </button>
      </div>
    );
  }

  const title = (routine.title as string) || "Generated Routine";
  const goal = (routine.goal as string) || "";
  const sessions = (routine.sessions as Array<Record<string, unknown>>) || [];

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      {/* Back button */}
      <div className="fixed top-4 left-4 z-20">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 px-3 py-2 rounded-xl bg-neutral-900/80 backdrop-blur-md border border-neutral-800 text-neutral-400 hover:text-white text-sm font-medium transition-all hover:border-neutral-700"
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
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back
        </button>
      </div>

      {/* Header */}
      <div className="sticky top-0 z-10 bg-neutral-950/90 backdrop-blur-md border-b border-neutral-800/50">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <h1 className="text-lg font-bold text-white">{title}</h1>
          {goal && (
            <p className="text-sm text-neutral-400 mt-1">{goal}</p>
          )}
        </div>
      </div>

      {/* Sessions / Days */}
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {sessions.length > 0 ? (
          sessions.map((session, sIdx) => {
            const dayName = (session.day as string) || (session.name as string) || `Day ${sIdx + 1}`;
            const focus = (session.focus as string) || "";
            const exercises = (session.exercises as Array<Record<string, unknown>>) || [];

            return (
              <div
                key={sIdx}
                className="p-4 bg-neutral-800/50 border border-neutral-700 rounded-xl"
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-white">{dayName}</h3>
                  {focus && (
                    <span className="text-sm text-emerald-400 font-medium">
                      {focus}
                    </span>
                  )}
                </div>
                <div className="space-y-2">
                  {exercises.map((ex, exIdx) => (
                    <div
                      key={exIdx}
                      className="flex items-center justify-between py-2 border-b border-neutral-700/50 last:border-0"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-neutral-300">
                          {(ex.name as string) || (ex.exercise as string) || "Exercise"}
                        </span>
                        {ex.notes && (
                          <span className="text-xs text-neutral-500 italic">
                            ({ex.notes as string})
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-3">
                        {ex.suggested_weight_kg != null && (
                          <span className="text-sm text-emerald-400 font-mono">
                            {ex.suggested_weight_kg as number}kg
                          </span>
                        )}
                        <span className="text-sm text-neutral-400 font-mono">
                          {ex.sets && ex.reps
                            ? `${ex.sets} x ${ex.reps}`
                            : ex.sets
                            ? `${ex.sets} sets`
                            : ""}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })
        ) : (
          /* Fallback: render raw JSON if shape is unexpected */
          <pre className="p-4 bg-neutral-800/50 border border-neutral-700 rounded-xl text-sm text-neutral-300 overflow-x-auto whitespace-pre-wrap">
            {JSON.stringify(routine, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
