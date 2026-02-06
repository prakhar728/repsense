"use client";

import { useState, useEffect } from "react";
import { LoginScreen } from "../components/LoginScreen";
import { UploadScreen } from "../components/UploadScreen";
import { ChatLayout } from "../components/ChatLayout";
import { getMagic } from "../lib/magic";
import { getUserProfileStatus } from "../lib/api";

type View = "login" | "upload" | "chat";

export default function Home() {
  const [view, setView] = useState<View>("login");
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [userEmail, setUserEmail] = useState("");

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const magic = getMagic();
        const loggedIn = await magic.user.isLoggedIn();
        if (loggedIn) {
          const info = await magic.user.getInfo();
          setUserEmail(info.email || "");

          if (info.email) {
            const status = await getUserProfileStatus(info.email);
            setView(status.exists ? "chat" : "upload");
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

    try {
      const info = await getMagic().user.getInfo();
      if (info.email) {
        const status = await getUserProfileStatus(info.email);
        setView(status.exists ? "chat" : "upload");
      } else {
        setView("upload");
      }
    } catch {
      setView("upload");
    }
  };

  const handleCSVContinue = () => {
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
    // Don't go back to login from upload — just stay
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
        {view === "login" && <LoginScreen onLogin={handleLogin} />}

        {view === "upload" && (
          <UploadScreen userEmail={userEmail} onContinue={handleCSVContinue} onBack={handleBack} />
        )}
      </div>
    </main>
  );
}
