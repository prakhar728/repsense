"use client";

import { useState } from "react";
import { DetailedRoutine, RoutineSet } from "../lib/routineData";

interface RoutineViewProps {
  routine: DetailedRoutine;
}

const goalColors: Record<string, string> = {
  Strength: "bg-blue-500/20 text-blue-400",
  Hypertrophy: "bg-purple-500/20 text-purple-400",
  Recovery: "bg-amber-500/20 text-amber-400",
  "Fat Loss": "bg-rose-500/20 text-rose-400",
};

function SetBadge({ set, index }: { set: RoutineSet; index: number }) {
  if (set.type === "warmup") {
    return (
      <span className="inline-flex items-center justify-center w-8 h-8 rounded-md text-sm font-bold text-amber-400">
        W
      </span>
    );
  }
  if (set.type === "failure") {
    return (
      <span className="inline-flex items-center justify-center w-8 h-8 rounded-md text-sm font-bold text-red-400">
        F
      </span>
    );
  }
  return (
    <span className="inline-flex items-center justify-center w-8 h-8 rounded-md text-sm font-bold text-white">
      {index}
    </span>
  );
}

// Simple dumbbell icon for exercises
function ExerciseIcon() {
  return (
    <div className="w-10 h-10 rounded-full bg-neutral-800 border border-neutral-700 flex items-center justify-center shrink-0">
      <svg
        className="w-5 h-5 text-neutral-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M6.5 6.5v11M17.5 6.5v11M6.5 12h11M3.5 8.5v7M20.5 8.5v7" />
      </svg>
    </div>
  );
}

export function RoutineView({ routine }: RoutineViewProps) {
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);
  const selectedDay = routine.weeklyPlan[selectedDayIndex];

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-neutral-950/90 backdrop-blur-md border-b border-neutral-800/50">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-bold text-white flex-1 truncate">
              {routine.name}
            </h1>
            <span
              className={`px-2.5 py-1 text-xs font-semibold rounded-lg shrink-0 ${
                goalColors[routine.goalTag] || "bg-neutral-700 text-neutral-300"
              }`}
            >
              {routine.goalTag}
            </span>
          </div>
          <p className="text-sm text-neutral-500 mt-1">{routine.frequency}</p>
        </div>

        {/* Day tabs */}
        <div className="max-w-2xl mx-auto px-4 pb-3">
          <div className="flex gap-1 overflow-x-auto scrollbar-none">
            {routine.weeklyPlan.map((day, i) => (
              <button
                key={day.day}
                onClick={() => setSelectedDayIndex(i)}
                className={`
                  px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all
                  ${
                    i === selectedDayIndex
                      ? "bg-emerald-500 text-white"
                      : "bg-neutral-800/50 text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800"
                  }
                `}
              >
                {day.day}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Day header */}
      <div className="max-w-2xl mx-auto px-4 pt-6 pb-2">
        <p className="text-sm text-neutral-500 uppercase tracking-wider font-medium">
          {selectedDay.focus}
        </p>
      </div>

      {/* Exercise list */}
      <div className="max-w-2xl mx-auto px-4 pb-12">
        {selectedDay.exercises.map((exercise, exIdx) => {
          let workingIndex = 0;

          return (
            <div key={exIdx} className="mt-8">
              {/* Exercise header */}
              <div className="flex items-center gap-3 mb-4">
                <ExerciseIcon />
                <h3 className="text-base font-semibold text-white">
                  {exercise.name}
                </h3>
              </div>

              {/* Column headers */}
              <div className="flex items-center px-3 mb-1">
                <span className="w-20 text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Sets
                </span>
                <span className="flex-1 text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Weight & Reps
                </span>
              </div>

              {/* Set rows */}
              {exercise.sets.map((set, setIdx) => {
                if (set.type === "working") {
                  workingIndex++;
                }

                return (
                  <div
                    key={setIdx}
                    className={`flex items-center px-3 py-2.5 rounded-lg ${
                      setIdx % 2 === 1 ? "bg-neutral-800/40" : ""
                    }`}
                  >
                    <div className="w-20">
                      <SetBadge set={set} index={workingIndex} />
                    </div>
                    <div className="flex-1 text-sm text-neutral-200">
                      {set.weight} x {set.reps} reps
                    </div>
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}
