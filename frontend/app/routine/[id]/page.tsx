"use client";

import { useParams, useRouter } from "next/navigation";
import { getRoutineById } from "../../../lib/routineData";
import { RoutineView } from "../../../components/RoutineView";

export default function RoutinePage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const routine = getRoutineById(id);

  if (!routine) {
    return (
      <div className="min-h-screen bg-neutral-950 text-white flex flex-col items-center justify-center px-4">
        <p className="text-neutral-400 mb-4">Routine not found</p>
        <button
          onClick={() => router.back()}
          className="text-emerald-500 hover:text-emerald-400 text-sm font-medium transition-colors"
        >
          Go back
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Back button floating over the routine */}
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
      <RoutineView routine={routine} />
    </div>
  );
}
