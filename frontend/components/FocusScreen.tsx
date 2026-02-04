"use client";

import { useState } from "react";
import { Button } from "./ui/Button";
import { Card, CardContent, CardFooter } from "./ui/Card";
import { Modal } from "./ui/Modal";
import { Spinner } from "./ui/Spinner";
import { generateRoutinesFromGoal, GeneratedRoutine } from "../lib/api";

const focusPresets = [
  "Fat loss",
  "Strength",
  "Hypertrophy",
  "Recovery",
  "Consistency",
];

// Goal tag colors
const goalColors: Record<string, string> = {
  strength: "bg-blue-500/20 text-blue-400",
  hypertrophy: "bg-purple-500/20 text-purple-400",
  recovery: "bg-amber-500/20 text-amber-400",
  fat_loss: "bg-rose-500/20 text-rose-400",
  general_strength: "bg-blue-500/20 text-blue-400",
  muscle_growth: "bg-purple-500/20 text-purple-400",
};

interface FocusScreenProps {
  userEmail: string;
  onBack: () => void;
  onStartTraining: () => void;
}

export function FocusScreen({ userEmail, onBack, onStartTraining }: FocusScreenProps) {
  const [focus, setFocus] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<GeneratedRoutine | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [error, setError] = useState("");

  const handlePresetClick = (preset: string) => {
    setFocus((prev) => {
      const trimmed = prev.trim();
      if (trimmed) {
        return `${trimmed}, ${preset.toLowerCase()}`;
      }
      return preset;
    });
  };

  const handleGenerate = async () => {
    if (!focus.trim()) return;

    setIsGenerating(true);
    setResult(null);
    setError("");

    try {
      const data = await generateRoutinesFromGoal(userEmail, focus);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate routine");
    } finally {
      setIsGenerating(false);
    }
  };

  const routine = result?.routine;
  const frequency = routine?.duration?.days_per_week
    ? `${routine.duration.days_per_week} days/week`
    : routine?.sessions
    ? `${routine.sessions.length} sessions`
    : "";

  const goalLabel = routine?.goal
    ? routine.goal.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
    : "";

  const goalColorClass =
    goalColors[routine?.goal || ""] || "bg-emerald-500/20 text-emerald-400";

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-neutral-400 hover:text-white transition-colors mb-6 group"
          aria-label="Go back"
        >
          <svg
            className="w-5 h-5 group-hover:-translate-x-1 transition-transform"
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
          <span className="text-sm font-medium">Back</span>
        </button>
      </div>

      {/* Focus Input Section */}
      <Card variant="elevated" className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <svg
            className="w-5 h-5 text-emerald-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
            />
          </svg>
          <h2 className="text-xl font-bold text-white">
            What should your next phase focus on?
          </h2>
        </div>

        <CardContent>
          <textarea
            value={focus}
            onChange={(e) => setFocus(e.target.value)}
            placeholder="e.g. Build strength without burning out, Get back on track after inconsistency, Improve chest & shoulders..."
            className="w-full h-32 px-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-xl text-white placeholder-neutral-500 resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
          />

          {/* Preset Chips */}
          <div className="flex flex-wrap gap-2 mt-4">
            {focusPresets.map((preset) => (
              <button
                key={preset}
                onClick={() => handlePresetClick(preset)}
                className="px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 hover:border-neutral-600 rounded-lg text-sm text-neutral-300 hover:text-white transition-all active:scale-95"
              >
                {preset}
              </button>
            ))}
          </div>
        </CardContent>

        <CardFooter>
          <Button
            variant="primary"
            size="lg"
            onClick={handleGenerate}
            disabled={!focus.trim() || isGenerating}
            isLoading={isGenerating}
            className="w-full sm:w-auto"
          >
            {isGenerating ? "Generating..." : "Generate routine"}
          </Button>
        </CardFooter>
      </Card>

      {/* Error State */}
      {error && (
        <div className="p-4 mb-8 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Loading State */}
      {isGenerating && (
        <div className="text-center py-16">
          <div className="inline-flex items-center gap-3 px-6 py-4 bg-neutral-900 border border-neutral-800 rounded-2xl">
            <Spinner size="md" />
            <div className="text-left">
              <p className="text-white font-medium">
                Analyzing your training data…
              </p>
              <p className="text-neutral-400 text-sm">
                Generating a personalized routine based on your profile
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Generated Routine */}
      {routine && !isGenerating && (
        <div className="animate-in slide-in-from-bottom-4 fade-in duration-500">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            <h2 className="text-lg font-semibold text-white">
              Your Personalized Routine
            </h2>
          </div>

          <Card variant="elevated" className="ring-2 ring-emerald-500 border-emerald-500">
            <div className="flex items-start justify-between mb-3">
              <h3 className="text-lg font-bold text-white pr-2">
                {routine.title}
              </h3>
              {goalLabel && (
                <span
                  className={`px-2.5 py-1 text-xs font-semibold rounded-lg shrink-0 ${goalColorClass}`}
                >
                  {goalLabel}
                </span>
              )}
            </div>

            {frequency && (
              <div className="flex items-center gap-2 text-neutral-400 text-sm mb-3">
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
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <span>{frequency}</span>
              </div>
            )}

            {routine.level && (
              <p className="text-neutral-400 text-sm mb-4">
                Level: {routine.level.replace(/\b\w/g, (c) => c.toUpperCase())}
              </p>
            )}

            <CardFooter className="!mt-4 !pt-4 border-t border-neutral-800">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDetails(true)}
              >
                View details
              </Button>
              <Button variant="primary" size="sm" onClick={onStartTraining}>
                Start training
                <svg
                  className="w-4 h-4 ml-1"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}

      {/* Details Modal */}
      <Modal
        isOpen={showDetails && !!routine}
        onClose={() => setShowDetails(false)}
        title={routine?.title || ""}
        size="xl"
      >
        {routine && (
          <div>
            {/* Overview */}
            <div className="flex flex-wrap gap-3 mb-6">
              {goalLabel && (
                <span
                  className={`px-3 py-1.5 text-sm font-semibold rounded-lg ${goalColorClass}`}
                >
                  {goalLabel}
                </span>
              )}
              {frequency && (
                <span className="px-3 py-1.5 text-sm font-medium rounded-lg bg-neutral-800 text-neutral-300">
                  {frequency}
                </span>
              )}
              {routine.level && (
                <span className="px-3 py-1.5 text-sm font-medium rounded-lg bg-neutral-800 text-neutral-300">
                  {routine.level.replace(/\b\w/g, (c) => c.toUpperCase())}
                </span>
              )}
            </div>

            {/* Weekly Plan */}
            <h3 className="text-lg font-bold text-white mb-4">
              {routine.plan_type === "single_session" ? "Session Plan" : "Weekly Plan"}
            </h3>
            <div className="space-y-4">
              {routine.sessions.map((session) => (
                <div
                  key={session.day}
                  className="p-4 bg-neutral-800/50 border border-neutral-700 rounded-xl"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-white">{session.day}</h4>
                    <span className="text-sm text-emerald-400 font-medium">
                      {session.focus}
                    </span>
                  </div>
                  <div className="space-y-2">
                    {session.exercises.map((exercise, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between py-2 border-b border-neutral-700/50 last:border-0"
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-neutral-300">
                            {exercise.name}
                          </span>
                          {exercise.notes && (
                            <span className="text-xs text-neutral-500 italic">
                              ({exercise.notes})
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-3">
                          {exercise.suggested_weight_kg != null && (
                            <span className="text-sm text-emerald-400 font-mono">
                              {exercise.suggested_weight_kg}kg
                            </span>
                          )}
                          <span className="text-sm text-neutral-400 font-mono">
                            {exercise.sets} x {exercise.reps}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Modal Footer */}
            <div className="mt-6 pt-6 border-t border-neutral-800 flex justify-end gap-3">
              <Button variant="ghost" onClick={() => setShowDetails(false)}>
                Close
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  setShowDetails(false);
                  onStartTraining();
                }}
              >
                Start training
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
