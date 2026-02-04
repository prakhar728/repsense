"use client";

import { useState } from "react";
import { Button } from "./ui/Button";
import { Card, CardContent, CardFooter } from "./ui/Card";
import { Modal } from "./ui/Modal";
import { Spinner } from "./ui/Spinner";
import {
  generateRoutines,
  focusPresets,
  Routine,
  ParsedCSVData,
} from "../lib/mockData";

interface FocusScreenProps {
  csvData: ParsedCSVData;
  onBack: () => void;
  onStartTraining: () => void;
}

// Goal tag colors
const goalColors: Record<string, string> = {
  Strength: "bg-blue-500/20 text-blue-400",
  Hypertrophy: "bg-purple-500/20 text-purple-400",
  Recovery: "bg-amber-500/20 text-amber-400",
  "Fat Loss": "bg-rose-500/20 text-rose-400",
};

export function FocusScreen({ csvData, onBack, onStartTraining }: FocusScreenProps) {
  const [focus, setFocus] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [routines, setRoutines] = useState<Routine[]>([]);
  const [selectedRoutine, setSelectedRoutine] = useState<Routine | null>(null);
  const [detailsRoutine, setDetailsRoutine] = useState<Routine | null>(null);

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
    setRoutines([]);
    setSelectedRoutine(null);

    try {
      const generated = await generateRoutines(focus);
      setRoutines(generated);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSelectRoutine = (routine: Routine) => {
    setSelectedRoutine(routine);
  };

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
            {isGenerating ? "Generating..." : "Generate routines"}
          </Button>
        </CardFooter>
      </Card>

      {/* Loading State */}
      {isGenerating && (
        <div className="text-center py-16">
          <div className="inline-flex items-center gap-3 px-6 py-4 bg-neutral-900 border border-neutral-800 rounded-2xl">
            <Spinner size="md" />
            <div className="text-left">
              <p className="text-white font-medium">
                Analyzing fatigue & consistency…
              </p>
              <p className="text-neutral-400 text-sm">
                Generating personalized routines based on {csvData.workoutsDetected} workouts
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Generated Routines */}
      {routines.length > 0 && !isGenerating && (
        <div className="animate-in slide-in-from-bottom-4 fade-in duration-500">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            <h2 className="text-lg font-semibold text-white">
              Recommended Routines
            </h2>
            <span className="text-neutral-500 text-sm">
              ({routines.length} options)
            </span>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {routines.map((routine) => (
              <Card
                key={routine.id}
                variant="elevated"
                className={`transition-all duration-200 ${
                  selectedRoutine?.id === routine.id
                    ? "ring-2 ring-emerald-500 border-emerald-500"
                    : "hover:border-neutral-700"
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-bold text-white pr-2">
                    {routine.name}
                  </h3>
                  <span
                    className={`px-2.5 py-1 text-xs font-semibold rounded-lg shrink-0 ${
                      goalColors[routine.goalTag] ||
                      "bg-neutral-700 text-neutral-300"
                    }`}
                  >
                    {routine.goalTag}
                  </span>
                </div>

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
                  <span>{routine.frequency}</span>
                </div>

                <p className="text-neutral-400 text-sm mb-4 line-clamp-2">
                  {routine.rationale}
                </p>

                <CardFooter className="!mt-4 !pt-4 border-t border-neutral-800">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setDetailsRoutine(routine)}
                  >
                    View details
                  </Button>
                  <Button
                    variant={selectedRoutine?.id === routine.id ? "primary" : "secondary"}
                    size="sm"
                    onClick={() => handleSelectRoutine(routine)}
                  >
                    {selectedRoutine?.id === routine.id ? (
                      <>
                        <svg
                          className="w-4 h-4 mr-1"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                        Selected
                      </>
                    ) : (
                      "Select routine"
                    )}
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>

          {/* Start Training CTA */}
          {selectedRoutine && (
            <div className="mt-8 p-6 bg-gradient-to-r from-emerald-500/10 to-emerald-600/10 border border-emerald-500/30 rounded-2xl animate-in slide-in-from-bottom-2 fade-in duration-300">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div>
                  <p className="text-white font-semibold">
                    Ready to start {selectedRoutine.name}?
                  </p>
                  <p className="text-neutral-400 text-sm">
                    {selectedRoutine.frequency} • {selectedRoutine.estimatedDuration}
                  </p>
                </div>
                <Button variant="primary" size="lg" onClick={onStartTraining}>
                  Start training
                  <svg
                    className="w-5 h-5 ml-1"
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
              </div>
            </div>
          )}
        </div>
      )}

      {/* Details Modal */}
      <Modal
        isOpen={!!detailsRoutine}
        onClose={() => setDetailsRoutine(null)}
        title={detailsRoutine?.name || ""}
        size="xl"
      >
        {detailsRoutine && (
          <div>
            {/* Overview */}
            <div className="flex flex-wrap gap-3 mb-6">
              <span
                className={`px-3 py-1.5 text-sm font-semibold rounded-lg ${
                  goalColors[detailsRoutine.goalTag] ||
                  "bg-neutral-700 text-neutral-300"
                }`}
              >
                {detailsRoutine.goalTag}
              </span>
              <span className="px-3 py-1.5 text-sm font-medium rounded-lg bg-neutral-800 text-neutral-300">
                {detailsRoutine.frequency}
              </span>
              <span className="px-3 py-1.5 text-sm font-medium rounded-lg bg-neutral-800 text-neutral-300">
                {detailsRoutine.estimatedDuration}
              </span>
            </div>

            {/* Rationale */}
            <p className="text-neutral-300 mb-6">{detailsRoutine.rationale}</p>

            {/* Recovery Note */}
            <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl mb-6">
              <div className="flex items-start gap-3">
                <svg
                  className="w-5 h-5 text-amber-500 shrink-0 mt-0.5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <div>
                  <p className="text-amber-400 font-medium text-sm mb-1">
                    Recovery Note
                  </p>
                  <p className="text-neutral-400 text-sm">
                    {detailsRoutine.recoveryNote}
                  </p>
                </div>
              </div>
            </div>

            {/* Weekly Plan */}
            <h3 className="text-lg font-bold text-white mb-4">Weekly Plan</h3>
            <div className="space-y-4">
              {detailsRoutine.weeklyPlan.map((day) => (
                <div
                  key={day.day}
                  className="p-4 bg-neutral-800/50 border border-neutral-700 rounded-xl"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-white">{day.day}</h4>
                    <span className="text-sm text-emerald-400 font-medium">
                      {day.focus}
                    </span>
                  </div>
                  <div className="space-y-2">
                    {day.exercises.map((exercise, idx) => (
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
                        <span className="text-sm text-neutral-400 font-mono">
                          {exercise.sets} × {exercise.reps}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Modal Footer */}
            <div className="mt-6 pt-6 border-t border-neutral-800 flex justify-end gap-3">
              <Button variant="ghost" onClick={() => setDetailsRoutine(null)}>
                Close
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  handleSelectRoutine(detailsRoutine);
                  setDetailsRoutine(null);
                }}
              >
                Select this routine
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
