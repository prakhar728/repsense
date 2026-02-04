"use client";

import { useState, useEffect } from "react";
import { LoginScreen } from "../components/LoginScreen";
import { UploadScreen } from "../components/UploadScreen";
import { FocusScreen } from "../components/FocusScreen";
import { ChatLayout } from "../components/ChatLayout";
import { ProgressIndicator } from "../components/ProgressIndicator";
import { ParsedCSVData } from "../lib/mockData";
import { getMagic } from "../lib/magic";

type View = "login" | "upload" | "focus" | "chat";

export default function Home() {
  const [view, setView] = useState<View>("login");
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [csvData, setCsvData] = useState<ParsedCSVData | null>(null);
  const [userEmail, setUserEmail] = useState("");

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const magic = getMagic();
        const loggedIn = await magic.user.isLoggedIn();
        if (loggedIn) {
          const info = await magic.user.getInfo();
          setUserEmail(info.email || "");

          const hasOnboarded = localStorage.getItem("repsense_onboarded");
          if (hasOnboarded) {
            setView("chat");
          } else {
            setView("upload");
          }
        }
      } catch {
        // Not logged in
      } finally {
        setIsCheckingAuth(false);
      }
    };
    checkAuth();
  }, []);

  const handleLogin = async () => {
    try {
      const magic = getMagic();
      const info = await magic.user.getInfo();
      setUserEmail(info.email || "");
    } catch {
      // Fallback
    }

    const hasOnboarded = localStorage.getItem("repsense_onboarded");
    if (hasOnboarded) {
      setView("chat");
    } else {
      setView("upload");
    }
  };

  const handleCSVContinue = (data: ParsedCSVData) => {
    setCsvData(data);
    setView("focus");
  };

  const handleStartTraining = () => {
    localStorage.setItem("repsense_onboarded", "true");
    setView("chat");
  };

  const handleLogout = async () => {
    try {
      const magic = getMagic();
      await magic.user.logout();
    } catch {
      // Ignore
    }
    setUserEmail("");
    setView("login");
  };

  const handleBack = () => {
    if (view === "upload") {
      // Don't go back to login — just stay
    } else if (view === "focus") {
      setView("upload");
    }
  };

  if (isCheckingAuth) {
    return (
      <main className="min-h-screen bg-neutral-950 text-white flex items-center justify-center">
        <div className="fixed inset-0 bg-gradient-to-br from-emerald-950/20 via-neutral-950 to-neutral-950 pointer-events-none" />
        <div className="relative z-10 animate-pulse text-neutral-400">
          Loading...
        </div>
      </main>
    );
  }

  // Chat view is full-screen with its own layout
  if (view === "chat") {
    return <ChatLayout userEmail={userEmail} onLogout={handleLogout} />;
  }

  const isOnboarding = view === "upload" || view === "focus";
  const onboardingStep = view === "upload" ? 1 : 2;

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
        {/* Progress Indicator (only during onboarding) */}
        {isOnboarding && (
          <div className="fixed top-0 left-0 right-0 bg-neutral-950/80 backdrop-blur-md border-b border-neutral-800/50 z-20">
            <div className="max-w-4xl mx-auto">
              <ProgressIndicator currentStep={onboardingStep} totalSteps={2} />
            </div>
          </div>
        )}

        {/* Content area */}
        <div className={isOnboarding ? "pt-16" : ""}>
          {view === "login" && <LoginScreen onLogin={handleLogin} />}

          {view === "upload" && (
            <UploadScreen userEmail={userEmail} onContinue={handleCSVContinue} onBack={handleBack} />
          )}

          {view === "focus" && csvData && (
            <FocusScreen
              csvData={csvData}
              onBack={handleBack}
              onStartTraining={handleStartTraining}
            />
          )}
        </div>
      </div>
    </main>
  );
}
