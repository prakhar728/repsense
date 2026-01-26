"use client";

import { useState } from "react";
import { LoginScreen } from "../components/LoginScreen";
import { UploadScreen } from "../components/UploadScreen";
import { FocusScreen } from "../components/FocusScreen";
import { ProgressIndicator } from "../components/ProgressIndicator";
import { ParsedCSVData } from "../lib/mockData";

type Step = 1 | 2 | 3;

export default function Home() {
  const [currentStep, setCurrentStep] = useState<Step>(1);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [csvData, setCsvData] = useState<ParsedCSVData | null>(null);

  const handleLogin = () => {
    setIsLoggedIn(true);
    setCurrentStep(2);
  };

  const handleCSVContinue = (data: ParsedCSVData) => {
    setCsvData(data);
    setCurrentStep(3);
  };

  const handleBack = () => {
    if (currentStep === 2) {
      setIsLoggedIn(false);
      setCurrentStep(1);
    } else if (currentStep === 3) {
      setCurrentStep(2);
    }
  };

  return (
    <main className="min-h-screen bg-neutral-950 text-white">
      {/* Background gradient effect */}
      <div className="fixed inset-0 bg-gradient-to-br from-emerald-950/20 via-neutral-950 to-neutral-950 pointer-events-none" />

      {/* Subtle grid pattern */}
      <div
        className="fixed inset-0 opacity-[0.02] pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}
      />

      <div className="relative z-10">
        {/* Progress Indicator (only show after login) */}
        {isLoggedIn && (
          <div className="fixed top-0 left-0 right-0 bg-neutral-950/80 backdrop-blur-md border-b border-neutral-800/50 z-20">
            <div className="max-w-4xl mx-auto">
              <ProgressIndicator currentStep={currentStep} totalSteps={3} />
            </div>
          </div>
        )}

        {/* Content area */}
        <div className={isLoggedIn ? "pt-16" : ""}>
          {currentStep === 1 && <LoginScreen onLogin={handleLogin} />}

          {currentStep === 2 && (
            <UploadScreen onContinue={handleCSVContinue} onBack={handleBack} />
          )}

          {currentStep === 3 && csvData && (
            <FocusScreen csvData={csvData} onBack={handleBack} />
          )}
        </div>
      </div>
    </main>
  );
}
