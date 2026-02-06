"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getUserRoutines, RoutineSummary } from "../../lib/api";
import { Spinner } from "../../components/ui/Spinner";
import { Modal } from "../../components/ui/Modal";
import { Button } from "../../components/ui/Button";
import { getMagic } from "../../lib/magic";

export default function RoutinesHistoryPage() {
  const [routines, setRoutines] = useState<RoutineSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<"auth" | "generic" | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [activeRoutine, setActiveRoutine] = useState<RoutineSummary | null>(null);
  const [userPrompt, setUserPrompt] = useState("");
  const router = useRouter();

  const titleCounts = routines.reduce<Record<string, number>>((acc, routine) => {
    const title = routine.title || "Generated Routine";
    acc[title] = (acc[title] || 0) + 1;
    return acc;
  }, {});

  const formatContextTitle = (routine: RoutineSummary) => {
    const title = routine.title || "Generated Routine";
    if ((titleCounts[title] || 0) <= 1) return title;
    const muscles = routine.focus_muscles?.slice(0, 2).join("/") || "General";
    const days = routine.days_per_week != null ? `${routine.days_per_week}d/wk` : "d/wk?";
    const date = new Date(routine.created_at).toLocaleDateString();
    return `${title} · ${muscles} · ${days} · ${date}`;
  };

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

  const openAddToChat = (routine: RoutineSummary) => {
    setActiveRoutine(routine);
    setUserPrompt("");
    setModalOpen(true);
  };

  const handleAddToChat = async () => {
    if (!activeRoutine) return;
    try {
      const magic = getMagic();
      const loggedIn = await magic.user.isLoggedIn();
      if (!loggedIn) {
        router.push("/");
        return;
      }
    } catch {
      router.push("/");
      return;
    }

    const focus = activeRoutine.focus_muscles?.length
      ? activeRoutine.focus_muscles.join(", ")
      : "unspecified";
    const days = activeRoutine.days_per_week ?? "unspecified";
    const title = activeRoutine.title || "Generated Routine";
    const goal = activeRoutine.goal || "unspecified";
    const prompt = userPrompt.trim() || "Use this routine as context.";

    const contextMessage = [
      `[[context:routine:${activeRoutine.id}]]`,
      `Title: ${title}`,
      `Goal: ${goal}`,
      `Days/Week: ${days}`,
      `Focus: ${focus}`,
      `[[/context]]`,
      prompt,
    ].join("\n");

    localStorage.setItem("repsense_pending_chat_message", contextMessage);
    setModalOpen(false);
    router.push("/");
  };

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
            <div
              key={routine.id}
              className="p-4 rounded-xl border border-neutral-800 bg-neutral-900/40 hover:bg-neutral-800/60 transition-all"
            >
              <div className="flex items-start justify-between gap-4">
                <Link href={`/routine/${routine.id}`} className="flex-1">
                  <h3 className="text-white font-semibold">
                    {formatContextTitle(routine)}
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
                </Link>
                <div className="flex flex-col items-end gap-3 shrink-0">
                  <span className="text-xs text-neutral-500">
                    {new Date(routine.created_at).toLocaleString()}
                  </span>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="border border-neutral-700 text-neutral-300 hover:text-white hover:border-neutral-500"
                    onClick={() => openAddToChat(routine)}
                  >
                    Add to chat
                  </Button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Add routine to chat"
      >
        <div className="space-y-4">
          <p className="text-sm text-neutral-400">
            Add a note so the agent uses this routine as context.
          </p>
          <textarea
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
            rows={4}
            className="w-full rounded-xl bg-neutral-950/60 border border-neutral-700 text-white px-4 py-3 text-sm focus:outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400"
            placeholder="e.g. Can you tweak this routine for my next 4-week block?"
          />
          <div className="flex justify-end gap-3">
            <Button variant="ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleAddToChat}>
              Send to chat
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
