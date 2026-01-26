"use client";

interface ProgressIndicatorProps {
  currentStep: number;
  totalSteps: number;
}

export function ProgressIndicator({
  currentStep,
  totalSteps,
}: ProgressIndicatorProps) {
  return (
    <div className="flex items-center justify-center gap-2 py-4">
      {Array.from({ length: totalSteps }).map((_, index) => {
        const stepNumber = index + 1;
        const isActive = stepNumber === currentStep;
        const isCompleted = stepNumber < currentStep;

        return (
          <div key={index} className="flex items-center">
            <div
              className={`
                w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-300
                ${
                  isActive
                    ? "bg-emerald-500 text-white scale-110"
                    : isCompleted
                    ? "bg-emerald-500/20 text-emerald-400"
                    : "bg-neutral-800 text-neutral-500"
                }
              `}
            >
              {isCompleted ? (
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2.5}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              ) : (
                stepNumber
              )}
            </div>
            {index < totalSteps - 1 && (
              <div
                className={`w-8 h-0.5 mx-1 transition-colors duration-300 ${
                  isCompleted ? "bg-emerald-500/50" : "bg-neutral-800"
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
